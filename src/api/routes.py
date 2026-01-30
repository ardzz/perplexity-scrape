"""
API routes for OpenAI-compatible REST API.
"""

import logging
from typing import Union

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from perplexity_client import PerplexityClient
from src.models.openai_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelListResponse,
    ModelInfo,
)
from src.models.model_mapping import list_available_models
from src.api.dependencies import get_client, get_api_key
from src.services.chat_completion_service import ChatCompletionService

logger = logging.getLogger(__name__)

# Create router with OpenAI-compatible prefix
router = APIRouter()


@router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
    response_model_exclude_none=True,
)
async def chat_completions(
    request: ChatCompletionRequest,
    client: PerplexityClient = Depends(get_client),
    api_key: str = Depends(get_api_key),
) -> Union[ChatCompletionResponse, StreamingResponse]:
    """
    Create a chat completion.

    This endpoint is compatible with the OpenAI Chat Completions API.
    It accepts the same request format and returns responses in the same format.

    - For non-streaming requests (stream=false), returns a complete ChatCompletionResponse.
    - For streaming requests (stream=true), returns SSE-formatted chunks.

    Note: All requests are processed in incognito mode and won't appear
    in your Perplexity dashboard.
    """
    logger.info(
        f"Chat completion request: model={request.model}, stream={request.stream}"
    )

    service = ChatCompletionService(client)
    return service.handle_request(request)


@router.get("/v1/models", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    """
    List available models.

    Returns a list of models available for chat completions.
    This endpoint is compatible with the OpenAI Models API.
    """
    models = [
        ModelInfo(id=model_id, owned_by="perplexity")
        for model_id in list_available_models()
    ]
    return ModelListResponse(data=models)


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Simple status object indicating the service is running.
    """
    return {"status": "ok", "service": "perplexity-openai-api"}
