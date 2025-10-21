import logging
logger = logging.getLogger(__name__)

import json
from anthropic.types.beta import BetaMessage

from cua.ai.tool_box import ToolBox
from cua.db.models import DB_Step, DB_ToolCall, ToolCallStatus, ContentType, StopReason
from cua.ai.client import anthropic_beta_request

from cua_protocol.schemas import AnthropicResponse


async def send_request(steps: list[DB_Step],
                       tool_box: ToolBox,
                       system_prompt: str,
                       instructions: str) -> DB_Step:
    if len(steps) == 0:
        raise ValueError("No agent loop steps provided")
    
    # Generate request messages including images for the last n_images_to_keep steps
    messages = _generate_messages(steps)
    
    # Send request
    anthropic_response: AnthropicResponse = await anthropic_beta_request(
            messages=messages,
            system_prompt=system_prompt,
            tools=await tool_box.get_anthropic_tool_definitions()
        )
    
    # Create new step object
    db_tool_calls = []
    for tool_call in anthropic_response.tool_calls or []:
        db_tool_calls.append(DB_ToolCall(
            call_id=tool_call.call_id,
            name=tool_call.name,
            input=tool_call.input,
            output_text="Tool call was aborted or not executed.",
        ))
    new_step = DB_Step(
        agent_loop_id=steps[-1].agent_loop_id,
        sequence=steps[-1].sequence + 1,
        response_content=anthropic_response.contents,
        response_text=anthropic_response.text,
        response_thinking_text=anthropic_response.thinking_text,
        tool_calls=db_tool_calls,
        end_turn=anthropic_response.end_turn,
    )
    
    return new_step

def _generate_messages(steps: list[DB_Step]) -> list[dict]:
    # Generate request messages including images for the last n_images_to_keep steps
    messages = []
    
    # # inject notes.md
    # notes_text = ""
    # lines = self._agent.notes.split('\n') if self._agent.notes else []
    # for i, line in enumerate(lines):
    #     notes_text += f"{i+1}: {line}\n"
    # notes_text = f"<injected_message>\nContents of notes.md:\n```\n{notes_text}\n```\n</injected_message>"
    # messages.append({"role": "user", "content": [{"type": "text", "text": notes_text}]})
    
    # create request messages from steps
    messages.extend(_steps_to_messages(steps, n_images_to_keep=20))

    # add cache control to last content block of last message
    try:
        messages[-1]["content"][-1]["cache_control"] = {"type": "ephemeral"}
    except (IndexError, KeyError):
        logger.error("Unable to add cache control to last message")

    return messages


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def _steps_to_messages(steps: list[DB_Step], n_images_to_keep: int = 20) -> list[dict]:
    messages = []
    
    n_steps = len(steps)
    for i, db_agent_loop_step in enumerate(steps):
        # Add response messages
        if db_agent_loop_step.response_content:
            messages.extend(db_agent_loop_step.response_content)
        
        # Generate and add request messages
        include_images = i >= n_steps - n_images_to_keep
        messages.extend(_generate_request_messages(db_agent_loop_step, include_images))

    return messages


def _generate_request_messages(db_agent_loop_step: DB_Step, include_images: bool = True) -> list:
    req_content = []
    
    # Add tool results to request_content
    for tool_call in db_agent_loop_step.tool_calls:
        req_content.append(_tool_call_to_message_content(tool_call, include_images))
    
    # Add user message to request_content
    if db_agent_loop_step.request_content:
        for content_block in db_agent_loop_step.request_content.content_list:
            if content_block.type == ContentType.TEXT:
                req_content.append({"type": "text", "text": content_block.content})
            elif content_block.type == ContentType.IMAGE:
                req_content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": content_block.content}})

    return [{"role": "user", "content": req_content}]


def _tool_call_to_message_content(db_tool_call: DB_ToolCall, include_images: bool = True) -> dict:
    tool_content = []
    
    if db_tool_call.status == ToolCallStatus.PENDING:
        tool_content.append({"type": "text", "text": "Interrupted: Tool call was aborted"})
    else:
        if db_tool_call.output_text:
            tool_content.append({"type": "text", "text": db_tool_call.output_text})
        if include_images and db_tool_call.output_base64_png_list:
            for base64_png in db_tool_call.output_base64_png_list:
                tool_content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_png}})
            
    return {"type": "tool_result", "tool_use_id": db_tool_call.call_id, "content": tool_content}