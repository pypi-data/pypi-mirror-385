from __future__ import annotations

import copy
import json
import os
import warnings
from collections.abc import Callable, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, ClassVar, Literal, get_args, get_origin

import httpx
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    SecretStr,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic.json_schema import SkipJsonSchema


if TYPE_CHECKING:  # type hints only, avoid runtime import cycle
    from openhands.sdk.tool.tool import ToolBase

from openhands.sdk.utils.pydantic_diff import pretty_pydantic_diff


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import litellm

from typing import cast

from litellm import (
    ChatCompletionToolParam,
    ResponseInputParam,
    completion as litellm_completion,
)
from litellm.exceptions import (
    APIConnectionError,
    BadRequestError,
    ContextWindowExceededError,
    InternalServerError,
    OpenAIError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout as LiteLLMTimeout,
)
from litellm.responses.main import responses as litellm_responses
from litellm.types.llms.openai import ResponsesAPIResponse
from litellm.types.utils import ModelResponse
from litellm.utils import (
    create_pretrained_tokenizer,
    get_model_info,
    supports_vision,
    token_counter,
)

from openhands.sdk.llm.exceptions import LLMNoResponseError

# OpenHands utilities
from openhands.sdk.llm.llm_response import LLMResponse
from openhands.sdk.llm.message import (
    Message,
)
from openhands.sdk.llm.mixins.non_native_fc import NonNativeToolCallingMixin
from openhands.sdk.llm.options.chat_options import select_chat_options
from openhands.sdk.llm.options.responses_options import select_responses_options
from openhands.sdk.llm.utils.metrics import Metrics, MetricsSnapshot
from openhands.sdk.llm.utils.model_features import get_features
from openhands.sdk.llm.utils.retry_mixin import RetryMixin
from openhands.sdk.llm.utils.telemetry import Telemetry
from openhands.sdk.logger import ENV_LOG_DIR, get_logger


logger = get_logger(__name__)

__all__ = ["LLM"]


# Exceptions we retry on
LLM_RETRY_EXCEPTIONS: tuple[type[Exception], ...] = (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
    LiteLLMTimeout,
    InternalServerError,
    LLMNoResponseError,
)

SERVICE_ID_DEPRECATION_MSG = (
    "LLM.service_id is deprecated and will be removed in a future release; "
    "use LLM.usage_id instead."
)


class LLM(BaseModel, RetryMixin, NonNativeToolCallingMixin):
    """Refactored LLM: simple `completion()`, centralized Telemetry, tiny helpers."""

    # =========================================================================
    # Config fields
    # =========================================================================
    model: str = Field(default="claude-sonnet-4-20250514", description="Model name.")
    api_key: SecretStr | None = Field(default=None, description="API key.")
    base_url: str | None = Field(default=None, description="Custom base URL.")
    api_version: str | None = Field(
        default=None, description="API version (e.g., Azure)."
    )

    aws_access_key_id: SecretStr | None = Field(default=None)
    aws_secret_access_key: SecretStr | None = Field(default=None)
    aws_region_name: str | None = Field(default=None)

    openrouter_site_url: str = Field(default="https://docs.all-hands.dev/")
    openrouter_app_name: str = Field(default="OpenHands")

    num_retries: int = Field(default=5, ge=0)
    retry_multiplier: float = Field(default=8.0, ge=0)
    retry_min_wait: int = Field(default=8, ge=0)
    retry_max_wait: int = Field(default=64, ge=0)

    timeout: int | None = Field(default=None, ge=0, description="HTTP timeout (s).")

    max_message_chars: int = Field(
        default=30_000,
        ge=1,
        description="Approx max chars in each event/content sent to the LLM.",
    )

    temperature: float | None = Field(default=0.0, ge=0)
    top_p: float | None = Field(default=1.0, ge=0, le=1)
    top_k: float | None = Field(default=None, ge=0)

    custom_llm_provider: str | None = Field(default=None)
    max_input_tokens: int | None = Field(
        default=None,
        ge=1,
        description="The maximum number of input tokens. "
        "Note that this is currently unused, and the value at runtime is actually"
        " the total tokens in OpenAI (e.g. 128,000 tokens for GPT-4).",
    )
    max_output_tokens: int | None = Field(
        default=None,
        ge=1,
        description="The maximum number of output tokens. This is sent to the LLM.",
    )
    input_cost_per_token: float | None = Field(
        default=None,
        ge=0,
        description="The cost per input token. This will available in logs for user.",
    )
    output_cost_per_token: float | None = Field(
        default=None,
        ge=0,
        description="The cost per output token. This will available in logs for user.",
    )
    ollama_base_url: str | None = Field(default=None)

    drop_params: bool = Field(default=True)
    modify_params: bool = Field(
        default=True,
        description="Modify params allows litellm to do transformations like adding"
        " a default message, when a message is empty.",
    )
    disable_vision: bool | None = Field(
        default=None,
        description="If model is vision capable, this option allows to disable image "
        "processing (useful for cost reduction).",
    )
    disable_stop_word: bool | None = Field(
        default=False, description="Disable using of stop word."
    )
    caching_prompt: bool = Field(default=True, description="Enable caching of prompts.")
    log_completions: bool = Field(
        default=False, description="Enable logging of completions."
    )
    log_completions_folder: str = Field(
        default=os.path.join(ENV_LOG_DIR, "completions"),
        description="The folder to log LLM completions to. "
        "Required if log_completions is True.",
    )
    custom_tokenizer: str | None = Field(
        default=None, description="A custom tokenizer to use for token counting."
    )
    native_tool_calling: bool | None = Field(
        default=None,
        description="Whether to use native tool calling "
        "if supported by the model. Can be True, False, or not set.",
    )
    reasoning_effort: Literal["low", "medium", "high", "none"] | None = Field(
        default=None,
        description="The effort to put into reasoning. "
        "This is a string that can be one of 'low', 'medium', 'high', or 'none'. "
        "Can apply to all reasoning models.",
    )
    enable_encrypted_reasoning: bool = Field(
        default=False,
        description="If True, ask for ['reasoning.encrypted_content'] "
        "in Responses API include.",
    )
    extended_thinking_budget: int | None = Field(
        default=200_000,
        description="The budget tokens for extended thinking, "
        "supported by Anthropic models.",
    )
    seed: int | None = Field(
        default=None, description="The seed to use for random number generation."
    )
    safety_settings: list[dict[str, str]] | None = Field(
        default=None,
        description=(
            "Safety settings for models that support them (like Mistral AI and Gemini)"
        ),
    )
    usage_id: str = Field(
        default="default",
        validation_alias=AliasChoices("usage_id", "service_id"),
        serialization_alias="usage_id",
        description=(
            "Unique usage identifier for the LLM. Used for registry lookups, "
            "telemetry, and spend tracking."
        ),
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Additional metadata for the LLM instance. "
            "Example structure: "
            "{'trace_version': '1.0.0', 'tags': ['model:gpt-4', 'agent:my-agent'], "
            "'session_id': 'session-123', 'trace_user_id': 'user-456'}"
        ),
    )

    # =========================================================================
    # Internal fields (excluded from dumps)
    # =========================================================================
    retry_listener: SkipJsonSchema[Callable[[int, int], None] | None] = Field(
        default=None,
        exclude=True,
    )
    _metrics: Metrics | None = PrivateAttr(default=None)
    # ===== Plain class vars (NOT Fields) =====
    # When serializing, these fields (SecretStr) will be dump to "****"
    # When deserializing, these fields will be ignored and we will override
    # them from the LLM instance provided at runtime.
    OVERRIDE_ON_SERIALIZE: tuple[str, ...] = (
        "api_key",
        "aws_access_key_id",
        "aws_secret_access_key",
    )

    # Runtime-only private attrs
    _model_info: Any = PrivateAttr(default=None)
    _tokenizer: Any = PrivateAttr(default=None)
    _function_calling_active: bool = PrivateAttr(default=False)
    _telemetry: Telemetry | None = PrivateAttr(default=None)

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", arbitrary_types_allowed=True
    )

    # =========================================================================
    # Validators
    # =========================================================================
    @field_validator("api_key", mode="before")
    @classmethod
    def _validate_api_key(cls, v):
        """Convert empty API keys to None to allow boto3 to use alternative auth methods."""  # noqa: E501
        if v is None:
            return None

        # Handle both SecretStr and string inputs
        if isinstance(v, SecretStr):
            secret_value = v.get_secret_value()
        else:
            secret_value = str(v)

        # If the API key is empty or whitespace-only, return None
        if not secret_value or not secret_value.strip():
            return None

        return v

    @model_validator(mode="before")
    @classmethod
    def _coerce_inputs(cls, data):
        if not isinstance(data, dict):
            return data
        d = dict(data)

        if "service_id" in d and "usage_id" not in d:
            warnings.warn(
                SERVICE_ID_DEPRECATION_MSG,
                DeprecationWarning,
                stacklevel=3,
            )
            d["usage_id"] = d.pop("service_id")

        model_val = d.get("model")
        if not model_val:
            raise ValueError("model must be specified in LLM")

        # default reasoning_effort unless Gemini 2.5
        # (we keep consistent with old behavior)
        excluded_models = ["gemini-2.5-pro", "claude-sonnet-4-5", "claude-haiku-4-5"]
        if d.get("reasoning_effort") is None and not any(
            model in model_val for model in excluded_models
        ):
            d["reasoning_effort"] = "high"

        # Azure default version
        if model_val.startswith("azure") and not d.get("api_version"):
            d["api_version"] = "2024-12-01-preview"

        # Provider rewrite: openhands/* -> litellm_proxy/*
        if model_val.startswith("openhands/"):
            model_name = model_val.removeprefix("openhands/")
            d["model"] = f"litellm_proxy/{model_name}"
            d["base_url"] = "https://llm-proxy.app.all-hands.dev/"

        # HF doesn't support the OpenAI default value for top_p (1)
        if model_val.startswith("huggingface"):
            if d.get("top_p", 1.0) == 1.0:
                d["top_p"] = 0.9

        return d

    @model_validator(mode="after")
    def _set_env_side_effects(self):
        if self.openrouter_site_url:
            os.environ["OR_SITE_URL"] = self.openrouter_site_url
        if self.openrouter_app_name:
            os.environ["OR_APP_NAME"] = self.openrouter_app_name
        if self.aws_access_key_id:
            os.environ["AWS_ACCESS_KEY_ID"] = self.aws_access_key_id.get_secret_value()
        if self.aws_secret_access_key:
            os.environ["AWS_SECRET_ACCESS_KEY"] = (
                self.aws_secret_access_key.get_secret_value()
            )
        if self.aws_region_name:
            os.environ["AWS_REGION_NAME"] = self.aws_region_name

        # Metrics + Telemetry wiring
        if self._metrics is None:
            self._metrics = Metrics(model_name=self.model)

        self._telemetry = Telemetry(
            model_name=self.model,
            log_enabled=self.log_completions,
            log_dir=self.log_completions_folder if self.log_completions else None,
            input_cost_per_token=self.input_cost_per_token,
            output_cost_per_token=self.output_cost_per_token,
            metrics=self._metrics,
        )

        # Tokenizer
        if self.custom_tokenizer:
            self._tokenizer = create_pretrained_tokenizer(self.custom_tokenizer)

        # Capabilities + model info
        self._init_model_info_and_caps()

        logger.debug(
            f"LLM ready: model={self.model} base_url={self.base_url} "
            f"reasoning_effort={self.reasoning_effort}"
        )
        return self

    # =========================================================================
    # Serializers
    # =========================================================================
    @field_serializer(
        "api_key", "aws_access_key_id", "aws_secret_access_key", when_used="always"
    )
    def _serialize_secrets(self, v: SecretStr | None, info):
        """Serialize secret fields, exposing actual values when expose_secrets context is True."""  # noqa: E501
        if v is None:
            return None

        # Check if the 'expose_secrets' flag is in the serialization context
        if info.context and info.context.get("expose_secrets"):
            return v.get_secret_value()

        # Let Pydantic handle the default masking
        return v

    # =========================================================================
    # Public API
    # =========================================================================
    @property
    def service_id(self) -> str:
        warnings.warn(
            SERVICE_ID_DEPRECATION_MSG,
            DeprecationWarning,
            stacklevel=2,
        )
        return self.usage_id

    @service_id.setter
    def service_id(self, value: str) -> None:
        warnings.warn(
            SERVICE_ID_DEPRECATION_MSG,
            DeprecationWarning,
            stacklevel=2,
        )
        self.usage_id = value

    @property
    def metrics(self) -> Metrics:
        assert self._metrics is not None, (
            "Metrics should be initialized after model validation"
        )
        return self._metrics

    def restore_metrics(self, metrics: Metrics) -> None:
        # Only used by ConversationStats to seed metrics
        self._metrics = metrics

    def completion(
        self,
        messages: list[Message],
        tools: Sequence[ToolBase] | None = None,
        _return_metrics: bool = False,
        add_security_risk_prediction: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """Single entry point for LLM completion.

        Normalize → (maybe) mock tools → transport → postprocess.
        """
        # Check if streaming is requested
        if kwargs.get("stream", False):
            raise ValueError("Streaming is not supported")

        # 1) serialize messages
        formatted_messages = self.format_messages_for_llm(messages)

        # 2) choose function-calling strategy
        use_native_fc = self.is_function_calling_active()
        original_fncall_msgs = copy.deepcopy(formatted_messages)

        # Convert Tool objects to ChatCompletionToolParam once here
        cc_tools: list[ChatCompletionToolParam] = []
        if tools:
            cc_tools = [
                t.to_openai_tool(
                    add_security_risk_prediction=add_security_risk_prediction
                )
                for t in tools
            ]

        use_mock_tools = self.should_mock_tool_calls(cc_tools)
        if use_mock_tools:
            logger.debug(
                "LLM.completion: mocking function-calling via prompt "
                f"for model {self.model}"
            )
            formatted_messages, kwargs = self.pre_request_prompt_mock(
                formatted_messages, cc_tools or [], kwargs
            )

        # 3) normalize provider params
        # Only pass tools when native FC is active
        kwargs["tools"] = cc_tools if (bool(cc_tools) and use_native_fc) else None
        has_tools_flag = bool(cc_tools) and use_native_fc
        # Behavior-preserving: delegate to select_chat_options
        call_kwargs = select_chat_options(self, kwargs, has_tools=has_tools_flag)

        # 4) optional request logging context (kept small)
        assert self._telemetry is not None
        log_ctx = None
        if self._telemetry.log_enabled:
            log_ctx = {
                "messages": formatted_messages[:],  # already simple dicts
                "tools": tools,
                "kwargs": {k: v for k, v in call_kwargs.items()},
                "context_window": self.max_input_tokens,
            }
            if tools and not use_native_fc:
                log_ctx["raw_messages"] = original_fncall_msgs
        self._telemetry.on_request(log_ctx=log_ctx)

        # 5) do the call with retries
        @self.retry_decorator(
            num_retries=self.num_retries,
            retry_exceptions=LLM_RETRY_EXCEPTIONS,
            retry_min_wait=self.retry_min_wait,
            retry_max_wait=self.retry_max_wait,
            retry_multiplier=self.retry_multiplier,
            retry_listener=self.retry_listener,
        )
        def _one_attempt(**retry_kwargs) -> ModelResponse:
            assert self._telemetry is not None
            # Merge retry-modified kwargs (like temperature) with call_kwargs
            final_kwargs = {**call_kwargs, **retry_kwargs}
            resp = self._transport_call(messages=formatted_messages, **final_kwargs)
            raw_resp: ModelResponse | None = None
            if use_mock_tools:
                raw_resp = copy.deepcopy(resp)
                resp = self.post_response_prompt_mock(
                    resp, nonfncall_msgs=formatted_messages, tools=cc_tools
                )
            # 6) telemetry
            self._telemetry.on_response(resp, raw_resp=raw_resp)

            # Ensure at least one choice
            if not resp.get("choices") or len(resp["choices"]) < 1:
                raise LLMNoResponseError(
                    "Response choices is less than 1. Response: " + str(resp)
                )

            return resp

        try:
            resp = _one_attempt()

            # Convert the first choice to an OpenHands Message
            first_choice = resp["choices"][0]
            message = Message.from_llm_chat_message(first_choice["message"])

            # Get current metrics snapshot
            metrics_snapshot = MetricsSnapshot(
                model_name=self.metrics.model_name,
                accumulated_cost=self.metrics.accumulated_cost,
                max_budget_per_task=self.metrics.max_budget_per_task,
                accumulated_token_usage=self.metrics.accumulated_token_usage,
            )

            # Create and return LLMResponse
            return LLMResponse(
                message=message, metrics=metrics_snapshot, raw_response=resp
            )
        except Exception as e:
            self._telemetry.on_error(e)
            raise

    # =========================================================================
    # Responses API (non-stream, v1)
    # =========================================================================
    def responses(
        self,
        messages: list[Message],
        tools: Sequence[ToolBase] | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        _return_metrics: bool = False,
        add_security_risk_prediction: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """Alternative invocation path using OpenAI Responses API via LiteLLM.

        Maps Message[] -> (instructions, input[]) and returns LLMResponse.
        Non-stream only for v1.
        """
        # Streaming not yet supported
        if kwargs.get("stream", False):
            raise ValueError("Streaming is not supported for Responses API yet")

        # Build instructions + input list using dedicated Responses formatter
        instructions, input_items = self.format_messages_for_responses(messages)

        # Convert Tool objects to Responses ToolParam
        # (Responses path always supports function tools)
        resp_tools = (
            [
                t.to_responses_tool(
                    add_security_risk_prediction=add_security_risk_prediction
                )
                for t in tools
            ]
            if tools
            else None
        )

        # Normalize/override Responses kwargs consistently
        call_kwargs = select_responses_options(
            self, kwargs, include=include, store=store
        )

        # Optional request logging
        assert self._telemetry is not None
        log_ctx = None
        if self._telemetry.log_enabled:
            log_ctx = {
                "llm_path": "responses",
                "input": input_items[:],
                "tools": tools,
                "kwargs": {k: v for k, v in call_kwargs.items()},
                "context_window": self.max_input_tokens,
            }
        self._telemetry.on_request(log_ctx=log_ctx)

        # Perform call with retries
        @self.retry_decorator(
            num_retries=self.num_retries,
            retry_exceptions=LLM_RETRY_EXCEPTIONS,
            retry_min_wait=self.retry_min_wait,
            retry_max_wait=self.retry_max_wait,
            retry_multiplier=self.retry_multiplier,
            retry_listener=self.retry_listener,
        )
        def _one_attempt(**retry_kwargs) -> ResponsesAPIResponse:
            final_kwargs = {**call_kwargs, **retry_kwargs}
            with self._litellm_modify_params_ctx(self.modify_params):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=DeprecationWarning)
                    typed_input: ResponseInputParam | str = (
                        cast(ResponseInputParam, input_items) if input_items else ""
                    )
                    ret = litellm_responses(
                        model=self.model,
                        input=typed_input,
                        instructions=instructions,
                        tools=resp_tools,
                        api_key=self.api_key.get_secret_value()
                        if self.api_key
                        else None,
                        api_base=self.base_url,
                        api_version=self.api_version,
                        timeout=self.timeout,
                        drop_params=self.drop_params,
                        seed=self.seed,
                        **final_kwargs,
                    )
                    assert isinstance(ret, ResponsesAPIResponse), (
                        f"Expected ResponsesAPIResponse, got {type(ret)}"
                    )
                    # telemetry (latency, cost). Token usage mapping we handle after.
                    assert self._telemetry is not None
                    self._telemetry.on_response(ret)
                    return ret

        try:
            resp: ResponsesAPIResponse = _one_attempt()

            # Parse output -> Message (typed)
            # Cast to a typed sequence
            # accepted by from_llm_responses_output
            output_seq = cast(Sequence[Any], resp.output or [])
            message = Message.from_llm_responses_output(output_seq)

            metrics_snapshot = MetricsSnapshot(
                model_name=self.metrics.model_name,
                accumulated_cost=self.metrics.accumulated_cost,
                max_budget_per_task=self.metrics.max_budget_per_task,
                accumulated_token_usage=self.metrics.accumulated_token_usage,
            )

            return LLMResponse(
                message=message, metrics=metrics_snapshot, raw_response=resp
            )
        except Exception as e:
            self._telemetry.on_error(e)
            raise

    # =========================================================================
    # Transport + helpers
    # =========================================================================
    def _transport_call(
        self, *, messages: list[dict[str, Any]], **kwargs
    ) -> ModelResponse:
        # litellm.modify_params is GLOBAL; guard it for thread-safety
        with self._litellm_modify_params_ctx(self.modify_params):
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", category=DeprecationWarning, module="httpx.*"
                )
                warnings.filterwarnings(
                    "ignore",
                    message=r".*content=.*upload.*",
                    category=DeprecationWarning,
                )
                warnings.filterwarnings(
                    "ignore",
                    message=r"There is no current event loop",
                    category=DeprecationWarning,
                )
                warnings.filterwarnings(
                    "ignore",
                    category=UserWarning,
                )
                # Some providers need renames handled in _normalize_call_kwargs.
                ret = litellm_completion(
                    model=self.model,
                    api_key=self.api_key.get_secret_value() if self.api_key else None,
                    base_url=self.base_url,
                    api_version=self.api_version,
                    timeout=self.timeout,
                    drop_params=self.drop_params,
                    seed=self.seed,
                    messages=messages,
                    **kwargs,
                )
                assert isinstance(ret, ModelResponse), (
                    f"Expected ModelResponse, got {type(ret)}"
                )
                return ret

    @contextmanager
    def _litellm_modify_params_ctx(self, flag: bool):
        old = getattr(litellm, "modify_params", None)
        try:
            litellm.modify_params = flag
            yield
        finally:
            litellm.modify_params = old

    # =========================================================================
    # Capabilities, formatting, and info
    # =========================================================================
    def _init_model_info_and_caps(self) -> None:
        # Try to get model info via openrouter or litellm proxy first
        tried = False
        try:
            if self.model.startswith("openrouter"):
                self._model_info = get_model_info(self.model)
                tried = True
        except Exception as e:
            logger.debug(f"get_model_info(openrouter) failed: {e}")

        if not tried and self.model.startswith("litellm_proxy/"):
            # IF we are using LiteLLM proxy, get model info from LiteLLM proxy
            # GET {base_url}/v1/model/info with litellm_model_id as path param
            base_url = self.base_url.strip() if self.base_url else ""
            if not base_url.startswith(("http://", "https://")):
                base_url = "http://" + base_url
            try:
                api_key = self.api_key.get_secret_value() if self.api_key else ""
                response = httpx.get(
                    f"{base_url}/v1/model/info",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                data = response.json().get("data", [])
                current = next(
                    (
                        info
                        for info in data
                        if info["model_name"]
                        == self.model.removeprefix("litellm_proxy/")
                    ),
                    None,
                )
                if current:
                    self._model_info = current.get("model_info")
                    logger.debug(
                        f"Got model info from litellm proxy: {self._model_info}"
                    )
            except Exception as e:
                logger.debug(f"Error fetching model info from proxy: {e}")

        # Fallbacks: try base name variants
        if not self._model_info:
            try:
                self._model_info = get_model_info(self.model.split(":")[0])
            except Exception:
                pass
        if not self._model_info:
            try:
                self._model_info = get_model_info(self.model.split("/")[-1])
            except Exception:
                pass

        # Context window and max_output_tokens
        if (
            self.max_input_tokens is None
            and self._model_info is not None
            and isinstance(self._model_info.get("max_input_tokens"), int)
        ):
            self.max_input_tokens = self._model_info.get("max_input_tokens")

        if self.max_output_tokens is None:
            if any(
                m in self.model
                for m in ["claude-3-7-sonnet", "claude-3.7-sonnet", "claude-sonnet-4"]
            ):
                self.max_output_tokens = (
                    64000  # practical cap (litellm may allow 128k with header)
                )
                logger.debug(
                    f"Setting max_output_tokens to {self.max_output_tokens} "
                    f"for {self.model}"
                )
            elif self._model_info is not None:
                if isinstance(self._model_info.get("max_output_tokens"), int):
                    self.max_output_tokens = self._model_info.get("max_output_tokens")
                elif isinstance(self._model_info.get("max_tokens"), int):
                    self.max_output_tokens = self._model_info.get("max_tokens")

        # Function-calling capabilities
        feats = get_features(self.model)
        logger.debug(f"Model features for {self.model}: {feats}")
        self._function_calling_active = (
            self.native_tool_calling
            if self.native_tool_calling is not None
            else feats.supports_function_calling
        )

    def vision_is_active(self) -> bool:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return not self.disable_vision and self._supports_vision()

    def _supports_vision(self) -> bool:
        """Acquire from litellm if model is vision capable.

        Returns:
            bool: True if model is vision capable. Return False if model not
                supported by litellm.
        """
        # litellm.supports_vision currently returns False for 'openai/gpt-...' or 'anthropic/claude-...' (with prefixes)  # noqa: E501
        # but model_info will have the correct value for some reason.
        # we can go with it, but we will need to keep an eye if model_info is correct for Vertex or other providers  # noqa: E501
        # remove when litellm is updated to fix https://github.com/BerriAI/litellm/issues/5608  # noqa: E501
        # Check both the full model name and the name after proxy prefix for vision support  # noqa: E501
        return (
            supports_vision(self.model)
            or supports_vision(self.model.split("/")[-1])
            or (
                self._model_info is not None
                and self._model_info.get("supports_vision", False)
            )
            or False  # fallback to False if model_info is None
        )

    def is_caching_prompt_active(self) -> bool:
        """Check if prompt caching is supported and enabled for current model.

        Returns:
            boolean: True if prompt caching is supported and enabled for the given
                model.
        """
        if not self.caching_prompt:
            return False
        # We don't need to look-up model_info, because
        # only Anthropic models need explicit caching breakpoints
        return self.caching_prompt and get_features(self.model).supports_prompt_cache

    def is_function_calling_active(self) -> bool:
        """Returns whether function calling is supported
        and enabled for this LLM instance.
        """
        return bool(self._function_calling_active)

    def uses_responses_api(self) -> bool:
        """Whether this model uses the OpenAI Responses API path."""

        # by default, uses = supports
        return get_features(self.model).supports_responses_api

    @property
    def model_info(self) -> dict | None:
        """Returns the model info dictionary."""
        return self._model_info

    # =========================================================================
    # Utilities preserved from previous class
    # =========================================================================
    def _apply_prompt_caching(self, messages: list[Message]) -> None:
        """Applies caching breakpoints to the messages.

        For new Anthropic API, we only need to mark the last user or
          tool message as cacheable.
        """
        if len(messages) > 0 and messages[0].role == "system":
            messages[0].content[-1].cache_prompt = True
        # NOTE: this is only needed for anthropic
        for message in reversed(messages):
            if message.role in ("user", "tool"):
                message.content[
                    -1
                ].cache_prompt = True  # Last item inside the message content
                break

    def format_messages_for_llm(self, messages: list[Message]) -> list[dict]:
        """Formats Message objects for LLM consumption."""

        messages = copy.deepcopy(messages)
        if self.is_caching_prompt_active():
            self._apply_prompt_caching(messages)

        for message in messages:
            message.cache_enabled = self.is_caching_prompt_active()
            message.vision_enabled = self.vision_is_active()
            message.function_calling_enabled = self.is_function_calling_active()
            if "deepseek" in self.model or (
                "kimi-k2-instruct" in self.model and "groq" in self.model
            ):
                message.force_string_serializer = True

        formatted_messages = [message.to_chat_dict() for message in messages]

        return formatted_messages

    def format_messages_for_responses(
        self, messages: list[Message]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Prepare (instructions, input[]) for the OpenAI Responses API.

        - Skips prompt caching flags and string serializer concerns
        - Uses Message.to_responses_value to get either instructions (system)
         or input items (others)
        - Concatenates system instructions into a single instructions string
        """
        msgs = copy.deepcopy(messages)

        # Set only vision flag; skip cache_enabled and force_string_serializer
        vision_active = self.vision_is_active()
        for m in msgs:
            m.vision_enabled = vision_active

        # Assign system instructions as a string, collect input items
        instructions: str | None = None
        input_items: list[dict[str, Any]] = []
        for m in msgs:
            val = m.to_responses_value(vision_enabled=vision_active)
            if isinstance(val, str):
                s = val.strip()
                if not s:
                    continue
                instructions = (
                    s if instructions is None else f"{instructions}\n\n---\n\n{s}"
                )
            else:
                if val:
                    input_items.extend(val)
        return instructions, input_items

    def get_token_count(self, messages: list[Message]) -> int:
        logger.debug(
            "Message objects now include serialized tool calls in token counting"
        )
        formatted_messages = self.format_messages_for_llm(messages)
        try:
            return int(
                token_counter(
                    model=self.model,
                    messages=formatted_messages,
                    custom_tokenizer=self._tokenizer,
                )
            )
        except Exception as e:
            logger.error(
                f"Error getting token count for model {self.model}\n{e}"
                + (
                    f"\ncustom_tokenizer: {self.custom_tokenizer}"
                    if self.custom_tokenizer
                    else ""
                ),
                exc_info=True,
            )
            return 0

    # =========================================================================
    # Serialization helpers
    # =========================================================================
    @classmethod
    def load_from_json(cls, json_path: str) -> LLM:
        with open(json_path) as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def load_from_env(cls, prefix: str = "LLM_") -> LLM:
        TRUTHY = {"true", "1", "yes", "on"}

        def _unwrap_type(t: Any) -> Any:
            origin = get_origin(t)
            if origin is None:
                return t
            args = [a for a in get_args(t) if a is not type(None)]
            return args[0] if args else t

        def _cast_value(raw: str, t: Any) -> Any:
            t = _unwrap_type(t)
            if t is SecretStr:
                return SecretStr(raw)
            if t is bool:
                return raw.lower() in TRUTHY
            if t is int:
                try:
                    return int(raw)
                except ValueError:
                    return None
            if t is float:
                try:
                    return float(raw)
                except ValueError:
                    return None
            origin = get_origin(t)
            if (origin in (list, dict, tuple)) or (
                isinstance(t, type) and issubclass(t, BaseModel)
            ):
                try:
                    return json.loads(raw)
                except Exception:
                    pass
            return raw

        data: dict[str, Any] = {}
        fields: dict[str, Any] = {
            name: f.annotation
            for name, f in cls.model_fields.items()
            if not getattr(f, "exclude", False)
        }

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            field_name = key[len(prefix) :].lower()
            if field_name not in fields:
                continue
            v = _cast_value(value, fields[field_name])
            if v is not None:
                data[field_name] = v
        return cls(**data)

    def resolve_diff_from_deserialized(self, persisted: LLM) -> LLM:
        """Resolve differences between a deserialized LLM and the current instance.

        This is due to fields like api_key being serialized to "****" in dumps,
        and we want to ensure that when loading from a file, we still use the
        runtime-provided api_key in the self instance.

        Return a new LLM instance equivalent to `persisted` but with
        explicitly whitelisted fields (e.g. api_key) taken from `self`.
        """
        if persisted.__class__ is not self.__class__:
            raise ValueError(
                f"Cannot resolve_diff_from_deserialized between {self.__class__} "
                f"and {persisted.__class__}"
            )

        # Copy allowed fields from runtime llm into the persisted llm
        llm_updates = {}
        persisted_dump = persisted.model_dump(exclude_none=True)
        for field in self.OVERRIDE_ON_SERIALIZE:
            if field in persisted_dump.keys():
                llm_updates[field] = getattr(self, field)
        if llm_updates:
            reconciled = persisted.model_copy(update=llm_updates)
        else:
            reconciled = persisted

        if self.model_dump(exclude_none=True) != reconciled.model_dump(
            exclude_none=True
        ):
            raise ValueError(
                "The LLM provided is different from the one in persisted state.\n"
                f"Diff: {pretty_pydantic_diff(self, reconciled)}"
            )
        return reconciled

    @staticmethod
    def is_context_window_exceeded_exception(exception: Exception) -> bool:
        """Check if the exception indicates a context window exceeded error.

        Context window exceeded errors vary by provider, and LiteLLM does not do a
        consistent job of identifying and wrapping them.
        """
        # A context window exceeded error from litellm is the best signal we have.
        if isinstance(exception, ContextWindowExceededError):
            return True

        # But with certain providers the exception might be a bad request or generic
        # OpenAI error, and we have to use the content of the error to figure out what
        # is wrong.
        if not isinstance(exception, (BadRequestError, OpenAIError)):
            return False

        # Not all BadRequestError or OpenAIError are context window exceeded errors, so
        # we need to check the message content for known patterns.
        error_string = str(exception).lower()

        known_exception_patterns: list[str] = [
            "contextwindowexceedederror",
            "prompt is too long",
            "input length and `max_tokens` exceed context limit",
            "please reduce the length of",
            "the request exceeds the available context size",
            "context length exceeded",
        ]

        if any(pattern in error_string for pattern in known_exception_patterns):
            return True

        # A special case for SambaNova, where multiple patterns are needed
        # simultaneously.
        samba_nova_patterns: list[str] = [
            "sambanovaexception",
            "maximum context length",
        ]

        if all(pattern in error_string for pattern in samba_nova_patterns):
            return True

        # If we've made it this far and haven't managed to positively ID it as a context
        # window exceeded error, we'll have to assume it's not and rely on the call-site
        # context to handle it appropriately.
        return False
