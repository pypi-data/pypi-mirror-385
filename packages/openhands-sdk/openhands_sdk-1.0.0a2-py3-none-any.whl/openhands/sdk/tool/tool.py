from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar, Protocol, Self, TypeVar

from litellm import (
    ChatCompletionToolParam,
    ChatCompletionToolParamFunctionChunk,
)
from openai.types.responses import FunctionToolParam
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
)
from pydantic.json_schema import SkipJsonSchema

from openhands.sdk.security import risk
from openhands.sdk.tool.schema import Action, Observation, Schema
from openhands.sdk.utils.models import (
    DiscriminatedUnionMixin,
    get_known_concrete_subclasses,
    kind_of,
)


ActionT = TypeVar("ActionT", bound=Action)
ObservationT = TypeVar("ObservationT", bound=Observation)
_action_types_with_risk: dict[type, type] = {}


class ToolAnnotations(BaseModel):
    """Annotations to provide hints about the tool's behavior.

    Based on Model Context Protocol (MCP) spec:
    https://github.com/modelcontextprotocol/modelcontextprotocol/blob/caf3424488b10b4a7b1f8cb634244a450a1f4400/schema/2025-06-18/schema.ts#L838
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        # We need to define the title here to avoid conflict with MCP's ToolAnnotations
        # when both are included in the same JSON schema for openapi.json
        title="openhands.sdk.tool.tool.ToolAnnotations",
    )

    title: str | None = Field(
        default=None, description="A human-readable title for the tool."
    )
    readOnlyHint: bool = Field(
        default=False,
        description="If true, the tool does not modify its environment. Default: false",
    )
    destructiveHint: bool = Field(
        default=True,
        description="If true, the tool may perform destructive updates to its environment. If false, the tool performs only additive updates. (This property is meaningful only when `readOnlyHint == false`) Default: true",  # noqa: E501
    )
    idempotentHint: bool = Field(
        default=False,
        description="If true, calling the tool repeatedly with the same arguments will have no additional effect on the its environment. (This property is meaningful only when `readOnlyHint == false`) Default: false",  # noqa: E501
    )
    openWorldHint: bool = Field(
        default=True,
        description="If true, this tool may interact with an 'open world' of external entities. If false, the tool's domain of interaction is closed. For example, the world of a web search tool is open, whereas that of a memory tool is not. Default: true",  # noqa: E501
    )


class ToolExecutor[ActionT, ObservationT](ABC):
    """Executor function type for a Tool."""

    @abstractmethod
    def __call__(self, action: ActionT) -> ObservationT:
        """Execute the tool with the given action and return an observation.

        Args:
            action: The action to execute, containing the parameters and context
                   needed for the tool operation.

        Returns:
            An observation containing the results of the tool execution.
        """

    def close(self) -> None:
        """Close the executor and clean up resources.

        Default implementation does nothing. Subclasses should override
        this method to perform cleanup (e.g., closing connections,
        terminating processes, etc.).
        """
        pass


class ExecutableTool(Protocol):
    """Protocol for tools that are guaranteed to have a non-None executor.

    This eliminates the need for runtime None checks and type narrowing
    when working with tools that are known to be executable.
    """

    name: str
    executor: ToolExecutor[Any, Any]  # Non-optional executor

    def __call__(self, action: Action) -> Observation:
        """Execute the tool with the given action."""
        ...


class ToolBase[ActionT, ObservationT](DiscriminatedUnionMixin, ABC):
    """Tool that wraps an executor function with input/output validation and schema.

    - Normalize input/output schemas (class or dict) into both model+schema.
    - Validate inputs before execute.
    - Coerce outputs only if an output model is defined; else return vanilla JSON.
    - Export MCP tool description.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True, arbitrary_types_allowed=True
    )

    name: str
    description: str
    action_type: type[Action] = Field(repr=False)
    observation_type: type[Observation] | None = Field(default=None, repr=False)

    annotations: ToolAnnotations | None = None
    meta: dict[str, Any] | None = None

    # runtime-only; always hidden on dumps
    executor: SkipJsonSchema[ToolExecutor | None] = Field(
        default=None, repr=False, exclude=True
    )

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Sequence[Self]:
        """Create a sequence of Tool instances. Placeholder for subclasses.

        This can be overridden in subclasses to provide custom initialization logic
            (e.g., typically initializing the executor with parameters).

        Returns:
            A sequence of Tool instances. Even single tools are returned as a sequence
            to provide a consistent interface and eliminate union return types.
        """

    @computed_field(return_type=str, alias="title")
    @property
    def title(self) -> str:
        if self.annotations and self.annotations.title:
            return self.annotations.title
        return self.name

    @field_serializer("action_type")
    def _ser_action_type(self, t: type[Action]) -> str:
        # serialize as a plain kind string
        return kind_of(t)

    @field_serializer("observation_type")
    def _ser_observation_type(self, t: type[Observation] | None) -> str | None:
        return None if t is None else kind_of(t)

    @field_validator("action_type", mode="before")
    @classmethod
    def _val_action_type(cls, v):
        if isinstance(v, str):
            return Action.resolve_kind(v)
        assert isinstance(v, type) and issubclass(v, Action), (
            f"action_type must be a subclass of Action, but got {type(v)}"
        )
        return v

    @field_validator("observation_type", mode="before")
    @classmethod
    def _val_observation_type(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = Observation.resolve_kind(v)
        assert isinstance(v, type) and issubclass(v, Observation), (
            f"observation_type must be a subclass of Observation, but got {type(v)}"
        )
        return v

    def set_executor(self, executor: ToolExecutor) -> Self:
        """Create a new Tool instance with the given executor."""
        return self.model_copy(update={"executor": executor})

    def as_executable(self) -> ExecutableTool:
        """Return this tool as an ExecutableTool, ensuring it has an executor.

        This method eliminates the need for runtime None checks by guaranteeing
        that the returned tool has a non-None executor.

        Returns:
            This tool instance, typed as ExecutableTool.

        Raises:
            NotImplementedError: If the tool has no executor.
        """
        if self.executor is None:
            raise NotImplementedError(f"Tool '{self.name}' has no executor")
        return self  # type: ignore[return-value]

    def action_from_arguments(self, arguments: dict[str, Any]) -> Action:
        """Create an action from parsed arguments.

        This method can be overridden by subclasses to provide custom logic
        for creating actions from arguments (e.g., for MCP tools).

        Args:
            arguments: The parsed arguments from the tool call.

        Returns:
            The action instance created from the arguments.
        """
        return self.action_type.model_validate(arguments)

    def __call__(self, action: ActionT) -> Observation:
        """Validate input, execute, and coerce output.

        We always return some Observation subclass, but not always the
        generic ObservationT.
        """
        if self.executor is None:
            raise NotImplementedError(f"Tool '{self.name}' has no executor")

        # Execute
        result = self.executor(action)

        # Coerce output only if we declared a model; else wrap in base Observation
        if self.observation_type:
            if isinstance(result, self.observation_type):
                return result
            return self.observation_type.model_validate(result)
        else:
            # When no output schema is defined, wrap the result in Observation
            if isinstance(result, Observation):
                return result
            elif isinstance(result, BaseModel):
                return Observation.model_validate(result.model_dump())
            elif isinstance(result, dict):
                return Observation.model_validate(result)
            raise TypeError(
                "Output must be dict or BaseModel when no output schema is defined"
            )

    def to_mcp_tool(
        self,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Convert a Tool to an MCP tool definition.

        Allow overriding input/output schemas (usually by subclasses).

        Args:
            input_schema: Optionally override the input schema.
            output_schema: Optionally override the output schema.
        """
        out = {
            "name": self.name,
            "description": self.description,
            "inputSchema": input_schema or self.action_type.to_mcp_schema(),
        }
        if self.annotations:
            out["annotations"] = self.annotations
        if self.meta is not None:
            out["_meta"] = self.meta

        derived_output = (
            output_schema
            if output_schema is not None
            else (
                self.observation_type.to_mcp_schema() if self.observation_type else None
            )
        )
        if derived_output is not None:
            out["outputSchema"] = derived_output
        return out

    def _get_tool_schema(
        self,
        add_security_risk_prediction: bool = False,
        action_type: type[Schema] | None = None,
    ) -> dict[str, Any]:
        action_type = action_type or self.action_type
        action_type_with_risk = _create_action_type_with_risk(action_type)

        add_security_risk_prediction = add_security_risk_prediction and (
            self.annotations is None or (not self.annotations.readOnlyHint)
        )
        schema = (
            action_type_with_risk.to_mcp_schema()
            if add_security_risk_prediction
            else action_type.to_mcp_schema()
        )
        return schema

    def to_openai_tool(
        self,
        add_security_risk_prediction: bool = False,
        action_type: type[Schema] | None = None,
    ) -> ChatCompletionToolParam:
        """Convert a Tool to an OpenAI tool.

        Args:
            add_security_risk_prediction: Whether to add a `security_risk` field
                to the action schema for LLM to predict. This is useful for
                tools that may have safety risks, so the LLM can reason about
                the risk level before calling the tool.
            action_type: Optionally override the action_type to use for the schema.
                This is useful for MCPTool to use a dynamically created action type
                based on the tool's input schema.
        """
        return ChatCompletionToolParam(
            type="function",
            function=ChatCompletionToolParamFunctionChunk(
                name=self.name,
                description=self.description,
                parameters=self._get_tool_schema(
                    add_security_risk_prediction, action_type
                ),
            ),
        )

    def to_responses_tool(
        self,
        add_security_risk_prediction: bool = False,
        action_type: type[Schema] | None = None,
    ) -> FunctionToolParam:
        """Convert a Tool to a Responses API function tool (LiteLLM typed).

        For Responses API, function tools expect top-level keys:
        { "type": "function", "name": ..., "description": ..., "parameters": ... }
        """

        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self._get_tool_schema(
                add_security_risk_prediction, action_type
            ),
            "strict": False,
        }

    @classmethod
    def resolve_kind(cls, kind: str) -> type:
        for subclass in get_known_concrete_subclasses(cls):
            if subclass.__name__ == kind:
                return subclass
        # Fallback to "ToolDefinition" for unknown type
        return ToolDefinition


class ToolDefinition[ActionT, ObservationT](ToolBase[ActionT, ObservationT]):
    """Concrete tool class that inherits from ToolBase.

    This class serves as a concrete implementation of ToolBase for cases where
    you want to create a tool instance directly without implementing a custom
    subclass. Built-in tools (like FinishTool, ThinkTool) are instantiated
    directly from this class, while more complex tools (like BashTool,
    FileEditorTool) inherit from this class and provide their own create()
    method implementations.
    """

    @classmethod
    def create(cls, *args, **kwargs) -> Sequence[Self]:
        """Create a sequence of ToolDefinition instances.

        TODO https://github.com/All-Hands-AI/agent-sdk/issues/493
        Refactor this - the ToolDefinition class should not have a concrete create()
        implementation. Built-in tools should be refactored to not rely on this
        method, and then this should be made abstract with @abstractmethod.
        """
        raise NotImplementedError(
            "ToolDefinition.create() should be implemented by subclasses"
        )


def _create_action_type_with_risk(action_type: type[Schema]) -> type[Schema]:
    action_type_with_risk = _action_types_with_risk.get(action_type)
    if action_type_with_risk:
        return action_type_with_risk

    action_type_with_risk = type(
        f"{action_type.__name__}WithRisk",
        (action_type,),
        {
            "security_risk": Field(
                # We do NOT add default value to make it an required field
                # default=risk.SecurityRisk.UNKNOWN
                description="The LLM's assessment of the safety risk of this action.",
            ),
            "__annotations__": {"security_risk": risk.SecurityRisk},
        },
    )
    _action_types_with_risk[action_type] = action_type_with_risk
    return action_type_with_risk
