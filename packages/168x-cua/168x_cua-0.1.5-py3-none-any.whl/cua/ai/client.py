import logging
logger = logging.getLogger(__name__)

from anthropic.types.beta import BetaMessage
import httpx

from cua.config import get_config

from cua_protocol.schemas import AnthropicRequest, AnthropicResponse

TIMEOUT = 10 * 60 # 10 minutes
ENDPOINT = "/v2/llm/anthropic-beta"

async def anthropic_beta_request(messages: list, system_prompt: str, tools: list[dict]) -> AnthropicResponse:
    config = get_config()
    
    anthropic_request = AnthropicRequest(
        agent_instance_id=config.agent_instance_id,
        secret_key=config.secret_key,
        messages=messages,
        system_prompt=system_prompt,
        tools=tools
    )
    
    # make http request
    response = await httpx.AsyncClient(timeout=TIMEOUT).post(
        config.backend_api_base_url + ENDPOINT,
        json=anthropic_request.model_dump(mode="json")
    )
    response.raise_for_status()
    return AnthropicResponse.model_validate(response.json())