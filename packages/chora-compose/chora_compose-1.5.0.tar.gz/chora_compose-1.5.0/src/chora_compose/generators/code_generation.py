"""AI-powered code generation using Anthropic Claude API."""

import logging
import os
import re
import time
from typing import Any

from anthropic import Anthropic, APIError, RateLimitError
from chora_compose.core.models import ContentConfig
from chora_compose.generators.base import GeneratorStrategy
from chora_compose.models import UpstreamDependencies
from chora_compose.telemetry import ContentGeneratedEvent, emit_event

logger = logging.getLogger(__name__)


class CodeGenerationError(Exception):
    """Raised when code generation fails."""

    pass


class CodeGenerationGenerator(GeneratorStrategy):
    """
    AI-powered code generation using Anthropic Claude API.

    This generator uses Claude to generate code based on prompts and context.
    It includes robust retry logic, cost tracking, and response parsing.

    Features:
    - Variable substitution in prompts
    - Language-specific formatting hints
    - Retry with exponential backoff
    - Response parsing (strips markdown fences)
    - Cost tracking per generation
    - Fallback template support

    Example config:
        {
            "type": "code_generation",
            "generation_config": {
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.0,
                "max_tokens": 4096,
                "prompt": "Generate {{language}} function that...",
                "language": "python",
                "style_hints": ["Use type hints", "Include docstrings"],
                "retry_count": 3,
                "retry_delay": 1.0,
                "timeout": 30.0,
                "fallback_template": "# TODO: Generation failed\\npass"
            }
        }
    """

    # Model pricing (per 1M tokens)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    }

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "claude-3-5-sonnet-20241022",
        default_temperature: float = 0.0,
        default_max_tokens: int = 4096,
        enable_cost_tracking: bool = True,
    ) -> None:
        """
        Initialize the code generation generator.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            default_model: Default Claude model to use
            default_temperature: Default temperature setting (0.0 = deterministic)
            default_max_tokens: Default maximum tokens in response
            enable_cost_tracking: Track API costs per generation

        Raises:
            CodeGenerationError: If API key not found
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise CodeGenerationError(
                "Anthropic API key not found. Please set ANTHROPIC_API_KEY "
                "environment variable or pass api_key parameter. "
                "Get your key at: https://console.anthropic.com/settings/keys"
            )

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)

        # Store defaults
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.enable_cost_tracking = enable_cost_tracking

        # Cost tracking
        self._total_cost = 0.0
        self._generation_count = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self.version = "0.9.0"
        self.description = "AI-powered code generation using Anthropic Claude models."
        self.capabilities = ["ai_powered", "code"]
        self.upstream_dependencies = UpstreamDependencies(
            services=["anthropic"],  # Requires Anthropic API
            credentials_required=["ANTHROPIC_API_KEY"],  # API key must be set
            expected_latency_ms={"p50": 1500, "p95": 5000},  # API call latency
            stability="stable",
            concurrency_safe=True,  # API supports concurrent requests
        )

    def generate(
        self, config: ContentConfig, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate code using Anthropic Claude API.

        Args:
            config: Content configuration with code_generation pattern
            context: Runtime context for prompt variable substitution

        Returns:
            Generated code as string

        Raises:
            CodeGenerationError: If generation fails after all retries
        """
        start_time = time.time()
        status = "success"
        error_message = None

        try:
            # Find code_generation pattern
            if not config.generation or not config.generation.patterns:
                raise CodeGenerationError(
                    f"Config '{config.id}' has no generation patterns defined"
                )

            code_gen_pattern = None
            for pattern in config.generation.patterns:
                if pattern.type == "code_generation":
                    code_gen_pattern = pattern
                    break

            if not code_gen_pattern:
                raise CodeGenerationError(
                    f"Config '{config.id}' has no code_generation pattern"
                )

            # Extract configuration
            gen_config = code_gen_pattern.generation_config or {}

            # Get configuration values with defaults
            model = gen_config.get("model", self.default_model)
            temperature = gen_config.get("temperature", self.default_temperature)
            max_tokens = gen_config.get("max_tokens", self.default_max_tokens)
            prompt_template = gen_config.get("prompt")
            language = gen_config.get("language")
            style_hints = gen_config.get("style_hints", [])
            system_prompt = gen_config.get("system_prompt")
            retry_count = gen_config.get("retry_count", 3)
            retry_delay = gen_config.get("retry_delay", 1.0)
            timeout = gen_config.get("timeout", 30.0)
            fallback_template: str | None = gen_config.get("fallback_template")  # type: ignore[assignment]

            if not prompt_template:
                raise CodeGenerationError(
                    f"Config '{config.id}' code_generation pattern missing "
                    f"'prompt' in generation_config"
                )

            # Merge context
            merged_context = {}
            if gen_config.get("context"):
                merged_context.update(gen_config["context"])
            if context:
                merged_context.update(context)

            # Build prompt
            prompt = self._build_prompt(
                prompt_template=prompt_template,
                context=merged_context,
                language=language,
                style_hints=style_hints,
            )

            # Call API with retry
            try:
                response, usage = self._call_api_with_retry(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    timeout=timeout,
                )

                # Track cost
                if self.enable_cost_tracking and usage:
                    self._track_cost(
                        model=model,
                        input_tokens=usage.get("input_tokens", 0),
                        output_tokens=usage.get("output_tokens", 0),
                    )

                # Parse response
                code = self._parse_response(response, language)

                return code

            except CodeGenerationError as e:
                # Use fallback if provided
                if fallback_template:
                    logger.error(
                        f"Code generation failed, using fallback template: {e}"
                    )
                    return fallback_template
                else:
                    raise

        except Exception as e:
            status = "error"
            error_message = str(e)
            raise
        finally:
            # Emit telemetry event
            duration_ms = int((time.time() - start_time) * 1000)
            emit_event(
                ContentGeneratedEvent(
                    content_config_id=config.id,
                    generator_type="code_generation",
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )
            )

    def _build_prompt(
        self,
        prompt_template: str,
        context: dict[str, Any],
        language: str | None,
        style_hints: list[str],
    ) -> str:
        """
        Build final prompt from template and context.

        Args:
            prompt_template: Template with {{variable}} placeholders
            context: Variable values
            language: Target programming language
            style_hints: Additional style guidance

        Returns:
            Complete prompt string
        """
        # Substitute variables in template
        prompt = prompt_template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            prompt = prompt.replace(placeholder, str(value))

        # Add language prefix if specified
        if language:
            prompt = f"Generate {language} code for:\n\n{prompt}"

        # Add style hints
        if style_hints:
            prompt += "\n\nStyle requirements:"
            for hint in style_hints:
                prompt += f"\n- {hint}"

        # Add standard suffix
        prompt += "\n\nProvide only the code, no explanations."

        return prompt

    def _call_api_with_retry(
        self,
        prompt: str,
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_tokens: int,
        retry_count: int,
        retry_delay: float,
        timeout: float,
    ) -> tuple[str, dict[str, int]]:
        """
        Call Anthropic API with exponential backoff retry.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model name
            temperature: Temperature setting
            max_tokens: Max tokens
            retry_count: Number of retries
            retry_delay: Initial delay between retries
            timeout: Request timeout

        Returns:
            Tuple of (response_text, usage_dict)

        Raises:
            CodeGenerationError: If all retries fail
        """
        last_error: Exception | None = None

        # Update client timeout
        self.client.timeout = timeout

        for attempt in range(retry_count + 1):
            try:
                # Call API
                message = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=(
                        system_prompt
                        or "You are an expert software developer. "
                        "Generate high-quality, production-ready code."
                    ),
                    messages=[{"role": "user", "content": prompt}],
                )

                # Extract response (ensure it's a TextBlock)
                content_block = message.content[0]
                if not hasattr(content_block, "text"):
                    raise CodeGenerationError(
                        f"Expected TextBlock, got {type(content_block).__name__}"
                    )
                response_text = content_block.text

                # Extract usage
                usage = {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                }

                return response_text, usage

            except RateLimitError as e:
                last_error = e
                if attempt < retry_count:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{retry_count + 1}), "
                        f"retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    raise CodeGenerationError(
                        f"Rate limit exceeded after {retry_count + 1} attempts"
                    ) from e

            except APIError as e:
                last_error = e
                if attempt < retry_count:
                    delay = retry_delay * (2**attempt)
                    logger.warning(
                        f"API error (attempt {attempt + 1}/{retry_count + 1}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    raise CodeGenerationError(
                        f"API error after {retry_count + 1} attempts: {e}"
                    ) from e

            except Exception as e:
                raise CodeGenerationError(
                    f"Unexpected error calling Anthropic API: {e}"
                ) from e

        # Should not reach here, but handle edge case
        raise CodeGenerationError(
            f"Code generation failed after {retry_count + 1} attempts. "
            f"Last error: {last_error}"
        )

    def _parse_response(self, response: str, language: str | None) -> str:
        """
        Parse and clean API response.

        Extracts code from markdown fences if present, otherwise returns as-is.

        Args:
            response: Raw API response
            language: Expected language (for fence detection)

        Returns:
            Clean code without markdown fences
        """
        # Try to extract code from markdown fences
        # Pattern: ```language\ncode\n```
        if language:
            pattern = rf"```{re.escape(language)}\n(.*?)\n```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)\n```"

        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            # Return first code block
            return str(matches[0]).strip()

        # Try generic fence without language
        pattern = r"```\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return str(matches[0]).strip()

        # No fences found, return as-is (stripped)
        return response.strip()

    def _track_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> dict[str, Any]:
        """
        Track API usage cost.

        Args:
            model: Model used
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            Cost breakdown dict
        """
        # Get pricing for model
        pricing = self.PRICING.get(model)
        if not pricing:
            logger.warning(f"No pricing info for model '{model}', cost not tracked")
            return {}

        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Update totals
        self._total_cost += total_cost
        self._generation_count += 1
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens

        cost_info = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
        }

        logger.info(
            f"Generation cost: ${total_cost:.6f} "
            f"(input: {input_tokens} tokens, output: {output_tokens} tokens)"
        )

        return cost_info

    def get_total_cost(self) -> dict[str, Any]:
        """
        Get cumulative cost tracking information.

        Returns:
            Dictionary with total costs and token counts
        """
        return {
            "total_cost_usd": round(self._total_cost, 6),
            "generation_count": self._generation_count,
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "average_cost_per_generation": (
                round(self._total_cost / self._generation_count, 6)
                if self._generation_count > 0
                else 0.0
            ),
        }

    def reset_cost_tracking(self) -> None:
        """Reset cost tracking counters."""
        self._total_cost = 0.0
        self._generation_count = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
