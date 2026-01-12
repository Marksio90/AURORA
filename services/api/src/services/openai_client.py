"""OpenAI client with retry logic and streaming support."""

from typing import Any

from openai import AsyncOpenAI, OpenAIError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core.config import settings
from src.core.errors import OpenAIException
from src.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API with retry logic."""

    def __init__(self) -> None:
        """Initialize OpenAI client with configuration."""
        if not settings.openai_api_key:
            logger.warning("openai_api_key_not_set")

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            max_retries=settings.openai_max_retries,
            timeout=settings.openai_timeout,
        )
        self.model = settings.openai_model
        self.embedding_model = settings.openai_embedding_model

    @retry(
        retry=retry_if_exception_type(OpenAIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> Any:
        """Create chat completion with retry logic.

        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            tools: Optional function calling tools
            tool_choice: How to handle tool calls

        Returns:
            OpenAI chat completion response

        Raises:
            OpenAIException: If API call fails after retries
        """
        try:
            logger.info(
                "openai_chat_request",
                model=self.model,
                message_count=len(messages),
                has_tools=tools is not None,
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                tool_choice=tool_choice if tools else None,
            )

            logger.info(
                "openai_chat_success",
                model=self.model,
                usage=response.usage.model_dump() if response.usage else None,
            )

            return response

        except OpenAIError as e:
            logger.error("openai_chat_error", error=str(e), model=self.model)
            raise OpenAIException(
                detail=f"OpenAI API error: {str(e)}",
                model=self.model,
            )

    @retry(
        retry=retry_if_exception_type(OpenAIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def create_embedding(
        self, text: str, model: str | None = None
    ) -> list[float]:
        """Create embedding vector for text.

        Args:
            text: Text to embed
            model: Optional model override

        Returns:
            Embedding vector (1536 dimensions for text-embedding-3-small)

        Raises:
            OpenAIException: If API call fails after retries
        """
        try:
            embedding_model = model or self.embedding_model

            logger.info(
                "openai_embedding_request",
                model=embedding_model,
                text_length=len(text),
            )

            response = await self.client.embeddings.create(
                model=embedding_model,
                input=text,
            )

            embedding = response.data[0].embedding

            logger.info(
                "openai_embedding_success",
                model=embedding_model,
                dimensions=len(embedding),
            )

            return embedding

        except OpenAIError as e:
            logger.error(
                "openai_embedding_error",
                error=str(e),
                model=embedding_model,
            )
            raise OpenAIException(
                detail=f"OpenAI embedding error: {str(e)}",
                model=embedding_model,
            )

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Any:
        """Create streaming chat completion.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Async stream of completion chunks

        Raises:
            OpenAIException: If stream fails
        """
        try:
            logger.info(
                "openai_stream_request",
                model=self.model,
                message_count=len(messages),
            )

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            return stream

        except OpenAIError as e:
            logger.error("openai_stream_error", error=str(e))
            raise OpenAIException(detail=f"OpenAI streaming error: {str(e)}")


# Global client instance
openai_client = OpenAIClient()
