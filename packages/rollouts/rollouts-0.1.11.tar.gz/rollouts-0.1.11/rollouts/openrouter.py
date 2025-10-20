"""
OpenRouter provider implementation.
"""

import os
import time
import asyncio
from typing import Optional, Dict, Any
import httpx
import json

from .datatypes import Response, Usage
from .types import GenerationConfig, APIResponse


class OpenRouter:
    """OpenRouter API provider for LLM generation.

    This class handles direct communication with the OpenRouter API,
    including request formatting, error handling, and response parsing.

    Attributes:
        api_key: The OpenRouter API key
        api_url: The OpenRouter API endpoint URL
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenRouter provider.

        Args:
            api_key: OpenRouter API key. If not provided, uses OPENROUTER_API_KEY
                environment variable.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_single(
        self,
        prompt: str,
        config: GenerationConfig,
        seed: Optional[int] = None,
        api_key: Optional[str] = None,
        rate_limiter=None,
    ) -> Response:
        """Generate a single response from the OpenRouter API.

        Args:
            prompt: The input prompt to send to the model
            config: Configuration dictionary containing model parameters
                (model, temperature, max_tokens, etc.)
            seed: Optional random seed for reproducible generation
            api_key: Optional API key to override instance key
            rate_limiter: Optional rate limiter to control request frequency

        Returns:
            Response object containing the generated text and metadata

        Note:
            This method includes automatic retry logic with exponential backoff
            for handling transient errors and rate limits.
        """
        # Use provided API key, fallback to instance key, then error if none
        key = api_key or self.api_key
        if not key:
            return self._error_response(
                "No API key provided. Pass api_key parameter or set OPENROUTER_API_KEY",
                config["model"],
            )

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://rollouts",
            "X-Title": "Rollouts Client",
        }

        # Format messages with model-specific thinking support
        from .think_handler import format_messages_with_thinking, debug_messages

        messages = format_messages_with_thinking(prompt, config["model"], config["verbose"])

        # Show formatted messages if verbose
        if config["verbose"]:
            debug_messages(messages, verbose=True)

        # Get all API parameters from config (excluding client-only settings)
        client_only = [
            "max_retries",
            "timeout",
            "verbose",
            "use_cache",
            "cache_dir",
            "requests_per_minute",
        ]
        payload = {k: v for k, v in config.items() if k not in client_only and v is not None}

        # Add messages (required)
        payload["messages"] = messages

        # Override seed if provided
        if seed is not None:
            payload["seed"] = seed

        # Retry logic
        retry_delay = 2
        for attempt in range(config["max_retries"]):
            try:
                # Apply rate limiting if configured
                if rate_limiter:
                    await rate_limiter.acquire()

                async with httpx.AsyncClient(timeout=config["timeout"]) as client:
                    response = await client.post(self.api_url, headers=headers, json=payload)

                    if response.status_code in [500, 429]:
                        if config["verbose"]:
                            error_type = (
                                "Server error" if response.status_code == 500 else "Rate limit"
                            )
                            print(f"{error_type} on attempt {attempt+1}/{config['max_retries']}")

                        delay = min(retry_delay * (2**attempt), 60)
                        await asyncio.sleep(delay)
                        continue

                    elif response.status_code != 200:
                        if config["verbose"]:
                            print(
                                f"API error ({response.status_code}) on attempt {attempt+1}/{config['max_retries']}. Returned json:\n{response.json()}"
                            )
                        if attempt == config["max_retries"] - 1:
                            return self._error_response(
                                f"API error: {response.status_code}", config["model"]
                            )
                        delay = min(retry_delay * (2**attempt), 60)
                        await asyncio.sleep(delay)
                        continue

                    try:
                        result = response.json()
                    except json.decoder.JSONDecodeError:
                        if config["verbose"]:
                            print(f"JSON decode error on attempt {attempt+1}/{config['max_retries']}. Returned response:\n{response}")
                        if attempt == config["max_retries"] - 1:
                            return self._error_response(
                                f"JSON decode error: {response.status_code}", config["model"]
                            )
                        delay = min(retry_delay * (2**attempt), 60)
                        continue

                    return self._parse_response(result, config["model"], seed)

            except (httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if config["verbose"]:
                    print(f"Request error on attempt {attempt+1}: {e}")

                if attempt == config["max_retries"] - 1:
                    return self._error_response(str(e), config["model"])

                delay = min(retry_delay * (2**attempt), 60)
                await asyncio.sleep(delay)

        return self._error_response("Max retries exceeded", config["model"])

    def _parse_response(self, result: Dict[str, Any], model: str, seed: Optional[int]) -> Response:
        """Parse API response into Response object.

        Args:
            result: Raw JSON response from OpenRouter API
            model: Model identifier used for the request
            seed: Random seed used for generation (if any)

        Returns:
            Response object with parsed content, reasoning, and metadata

        Note:
            Handles both reasoning and non-reasoning model responses,
            properly splitting content and reasoning text when present.
        """
        if "choices" not in result or len(result["choices"]) == 0:
            return self._error_response("No choices in response", model)

        choice = result["choices"][0]
        message = choice.get("message", {})

        # Handle reasoning/content split
        reasoning_text = message.get("reasoning", "")
        content_text = message.get("content", "")

        if reasoning_text and content_text:
            full = f"{reasoning_text}</think>{content_text}"
            completed_reasoning = True
        elif reasoning_text:
            full = reasoning_text
            completed_reasoning = False
        else:
            full = content_text
            completed_reasoning = True

        # Extract usage
        usage_data = result.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return Response(
            full=full,
            content=content_text,
            reasoning=reasoning_text,
            finish_reason=choice.get("finish_reason", ""),
            provider=result.get("provider", "OpenRouter"),
            response_id=result.get("id", ""),
            model=result.get("model", model),
            object=result.get("object", "chat.completion"),
            created=result.get("created", int(time.time())),
            usage=usage,
            logprobs=None,
            echo=False,
            seed=seed,
            completed_reasoning=completed_reasoning,
        )

    def _error_response(self, error_msg: str, model: str) -> Response:
        """Create an error response object.

        Args:
            error_msg: Error message describing what went wrong
            model: Model identifier that was requested

        Returns:
            Response object with finish_reason="error" and error message in full field

        Note:
            Error responses are not cached and will be regenerated on retry.
        """
        return Response(
            full=f"Error: {error_msg}",
            content="",
            reasoning="",
            finish_reason="error",
            provider="OpenRouter",
            response_id="",
            model=model,
            object="error",
            created=int(time.time()),
            usage=Usage(),
            logprobs=None,
            echo=False,
        )
