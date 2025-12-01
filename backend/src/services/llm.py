"""
LLM service for RAG Pipeline Query Endpoint.

This module implements LLM-based answer generation using OpenAI GPT-4 Turbo
with context grounding and refusal detection.

Services:
    - LLMService: Generates answers from retrieved context chunks

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule IV: Comprehensive error handling and logging
    - FR-004: LLM refusal detection
    - FR-015: 25-second timeout enforcement
"""

import asyncio
import re
from typing import List

from openai import AsyncOpenAI

from src.core.config import Settings
from src.core.exceptions import LLMServiceError, llm_timeout
from src.core.metrics import record_llm_generation_latency
from src.models.vector import VectorSearchResult
from src.services.logging import get_logger, log_llm_generation

logger = get_logger(__name__)


class LLMService:
    """
    Service for generating AI answers using OpenAI GPT-4 Turbo.

    Constructs grounded prompts from retrieved context chunks and generates
    answers with refusal detection per FR-004.

    Attributes:
        client: OpenAI async client
        settings: Application settings (model, timeouts, max_tokens)

    Example:
        >>> service = LLMService(openai_client, settings)
        >>> response = await service.generate_answer(
        ...     query_text="What are ROS 2 nodes?",
        ...     context_chunks=[chunk1, chunk2, chunk3],
        ...     temperature=0.7
        ... )
        >>> response.answer
        "ROS 2 nodes are the fundamental building blocks..."
        >>> response.refused
        False
    """

    # Refusal detection patterns per FR-004 (enhanced for relevance)
    REFUSAL_PATTERNS = [
        r"I don't have enough information",
        r"I don't know",
        r"irrelevant to the book",
        r"I cannot answer",
        r"insufficient information",
        r"not enough context",
        r"context does not contain",
        r"unable to answer",
        r"outside the scope",
        r"not covered in this",
    ]

    def __init__(self, client: AsyncOpenAI, settings: Settings) -> None:
        """
        Initialize LLM service.

        Args:
            client: Initialized OpenAI async client
            settings: Application settings
        """
        self.client = client
        self.settings = settings

    def _build_system_prompt(
        self,
        query_text: str,
        context_chunks: List[VectorSearchResult],
    ) -> str:
        """
        Build system prompt with context chunks.

        Constructs prompt per research.md Decision 3 with instruction to
        refuse if context insufficient (FR-004).

        Args:
            query_text: User's question
            context_chunks: Retrieved chunks from vector search

        Returns:
            System prompt string with formatted context

        Example:
            >>> prompt = service._build_system_prompt(
            ...     query_text="What are ROS 2 nodes?",
            ...     context_chunks=[chunk1, chunk2]
            ... )
            >>> "You are an expert tutor" in prompt
            True
        """
        # Format context chunks with numbering for clarity
        formatted_chunks = "\n\n".join(
            f"[{i+1}] {chunk.content}" for i, chunk in enumerate(context_chunks)
        )

        # System prompt template with stronger relevance enforcement
        system_prompt = f"""You are an expert tutor for a Physical AI & Humanoid Robotics textbook.

CRITICAL RULES:
1. Answer ONLY using the provided context chunks below
2. If the question is NOT about Physical AI, Humanoid Robotics, ROS 2, Isaac Sim, Gazebo, or VLA models, respond EXACTLY with:
   "I don't know. This question is irrelevant to the book."
3. If the question IS relevant but the context lacks sufficient information, respond with:
   "I don't have enough information in this chapter to answer that."
4. NEVER use external knowledge or speculation
5. Stay strictly within the book's scope: Physical AI, Humanoid Robotics, ROS 2, simulation, and VLA

Context chunks from the textbook:
{formatted_chunks}

Student Question: {query_text}

Answer:"""

        return system_prompt

    def _detect_refusal(self, answer: str) -> bool:
        """
        Detect if LLM explicitly refused to answer.

        Checks answer text against refusal patterns per FR-004.

        Args:
            answer: LLM-generated answer text

        Returns:
            True if LLM refused (insufficient context), False otherwise

        Example:
            >>> service._detect_refusal("I don't have enough information...")
            True
            >>> service._detect_refusal("ROS 2 nodes are...")
            False
        """
        answer_lower = answer.lower()
        for pattern in self.REFUSAL_PATTERNS:
            if re.search(pattern, answer_lower, re.IGNORECASE):
                return True
        return False

    async def generate_answer(
        self,
        query_text: str,
        context_chunks: List[VectorSearchResult],
        temperature: float = 0.7,
        query_id: str | None = None,
    ) -> dict[str, any]:
        """
        Generate answer from query and context chunks.

        Calls OpenAI GPT-4 Turbo with constructed prompt, enforces timeout
        per FR-015, and detects refusals per FR-004.

        Args:
            query_text: User's question
            context_chunks: Retrieved chunks from vector search
            temperature: LLM sampling temperature (0.0-1.0, default 0.7)
            query_id: Optional query ID for logging/metrics

        Returns:
            Dict with:
                - answer (str): Generated answer text
                - refused (bool): True if LLM explicitly refused
                - tokens_used (int): Total tokens consumed
                - model (str): Model used for generation

        Raises:
            LLMServiceError: If OpenAI API call fails or times out
            ValueError: If temperature out of range or no context chunks

        Example:
            >>> result = await service.generate_answer(
            ...     query_text="What are ROS 2 nodes?",
            ...     context_chunks=[chunk1, chunk2],
            ...     temperature=0.7
            ... )
            >>> result["answer"]
            "ROS 2 nodes are the fundamental building blocks..."
            >>> result["refused"]
            False
            >>> result["tokens_used"]
            456
        """
        # Validate inputs
        if not context_chunks:
            raise ValueError("Must provide at least one context chunk")

        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"Temperature must be 0.0-1.0, got {temperature}")

        # Build system prompt
        system_prompt = self._build_system_prompt(query_text, context_chunks)

        # Log generation start
        if query_id:
            logger.debug(
                f"Starting LLM generation for query_id={query_id}",
                extra={
                    "query_id": query_id,
                    "temperature": temperature,
                    "model": self.settings.llm_model,
                    "context_chunks": len(context_chunks),
                },
            )

        try:
            # Call OpenAI API with timeout enforcement (FR-015: 25 seconds)
            import time

            start_time = time.time()

            # Wrap OpenAI call in asyncio timeout
            completion_task = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                ],
                temperature=temperature,
                max_tokens=self.settings.llm_max_tokens,
                timeout=self.settings.llm_timeout,
            )

            completion = await asyncio.wait_for(
                completion_task,
                timeout=self.settings.llm_timeout,
            )

            # Calculate latency
            latency_seconds = time.time() - start_time
            latency_ms = int(latency_seconds * 1000)

            # Extract answer
            answer = completion.choices[0].message.content or ""

            # Detect refusal per FR-004
            refused = self._detect_refusal(answer)

            # Extract token usage
            tokens_used = completion.usage.total_tokens if completion.usage else 0

            # Record metrics
            record_llm_generation_latency(latency_seconds, self.settings.llm_model)

            # Log completion
            if query_id:
                log_llm_generation(
                    logger=logger,
                    query_id=query_id,
                    latency_ms=latency_ms,
                    model=self.settings.llm_model,
                    tokens_used=tokens_used,
                )

            logger.info(
                f"LLM generation completed: {tokens_used} tokens in {latency_ms}ms",
                extra={
                    "query_id": query_id,
                    "latency_ms": latency_ms,
                    "tokens_used": tokens_used,
                    "refused": refused,
                },
            )

            return {
                "answer": answer,
                "refused": refused,
                "tokens_used": tokens_used,
                "model": self.settings.llm_model,
            }

        except asyncio.TimeoutError:
            # FR-015: Handle timeout (25 seconds)
            logger.error(
                f"LLM generation timeout after {self.settings.llm_timeout}s",
                extra={
                    "query_id": query_id,
                    "timeout_seconds": self.settings.llm_timeout,
                },
            )
            raise llm_timeout(timeout_seconds=self.settings.llm_timeout)

        except Exception as e:
            # Handle other OpenAI API errors
            logger.error(
                f"LLM generation failed: {str(e)}",
                extra={
                    "query_id": query_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise LLMServiceError(
                message=f"LLM service failed: {str(e)}",
                details={
                    "model": self.settings.llm_model,
                    "temperature": temperature,
                },
            )


async def generate_answer(
    client: AsyncOpenAI,
    settings: Settings,
    query_text: str,
    context_chunks: List[VectorSearchResult],
    temperature: float = 0.7,
    query_id: str | None = None,
) -> dict[str, any]:
    """
    Convenience function for LLM answer generation.

    Creates LLMService instance and generates answer.
    Use this for one-off generation without managing service lifecycle.

    Args:
        client: OpenAI async client
        settings: Application settings
        query_text: User's question
        context_chunks: Retrieved chunks from vector search
        temperature: LLM sampling temperature (0.0-1.0, default 0.7)
        query_id: Optional query ID for logging

    Returns:
        Dict with answer, refused status, tokens_used, model

    Raises:
        LLMServiceError: If generation fails or times out

    Example:
        >>> from src.core.config import get_settings
        >>> result = await generate_answer(
        ...     client=openai_client,
        ...     settings=get_settings(),
        ...     query_text="What are ROS 2 nodes?",
        ...     context_chunks=[chunk1, chunk2]
        ... )
        >>> result["answer"]
        "ROS 2 nodes are..."
    """
    service = LLMService(client, settings)
    return await service.generate_answer(
        query_text=query_text,
        context_chunks=context_chunks,
        temperature=temperature,
        query_id=query_id,
    )
