import json

from pydantic import ValidationError

import openhands.sdk.security.risk as risk
from openhands.sdk.agent.base import AgentBase
from openhands.sdk.context.view import View
from openhands.sdk.conversation import ConversationCallbackType, ConversationState
from openhands.sdk.conversation.state import AgentExecutionStatus
from openhands.sdk.event import (
    ActionEvent,
    AgentErrorEvent,
    LLMConvertibleEvent,
    MessageEvent,
    ObservationEvent,
    SystemPromptEvent,
)
from openhands.sdk.event.condenser import Condensation, CondensationRequest
from openhands.sdk.llm import (
    Message,
    MessageToolCall,
    ReasoningItemModel,
    RedactedThinkingBlock,
    TextContent,
    ThinkingBlock,
)
from openhands.sdk.logger import get_logger
from openhands.sdk.security.confirmation_policy import NeverConfirm
from openhands.sdk.security.llm_analyzer import LLMSecurityAnalyzer
from openhands.sdk.tool import (
    Action,
    FinishTool,
    Observation,
)
from openhands.sdk.tool.builtins import FinishAction, ThinkAction


logger = get_logger(__name__)


class Agent(AgentBase):
    @property
    def _add_security_risk_prediction(self) -> bool:
        return isinstance(self.security_analyzer, LLMSecurityAnalyzer)

    def _configure_bash_tools_env_provider(self, state: ConversationState) -> None:
        """
        Configure bash tool with reference to secrets manager.
        Updated secrets automatically propagate.
        """

        secrets_manager = state.secrets_manager

        def env_for_cmd(cmd: str) -> dict[str, str]:
            try:
                return secrets_manager.get_secrets_as_env_vars(cmd)
            except Exception:
                return {}

        def env_masker(output: str) -> str:
            try:
                return secrets_manager.mask_secrets_in_output(output)
            except Exception:
                return ""

        execute_bash_exists = False
        for tool in self.tools_map.values():
            if tool.name == "execute_bash":
                try:
                    executable_tool = tool.as_executable()
                    # Wire the env provider and env masker for the bash executor
                    setattr(executable_tool.executor, "env_provider", env_for_cmd)
                    setattr(executable_tool.executor, "env_masker", env_masker)
                    execute_bash_exists = True
                except NotImplementedError:
                    # Tool has no executor, skip it
                    continue

        if not execute_bash_exists:
            logger.warning("Skipped wiring SecretsManager: missing bash tool")

    def init_state(
        self,
        state: ConversationState,
        on_event: ConversationCallbackType,
    ) -> None:
        super().init_state(state, on_event=on_event)
        # TODO(openhands): we should add test to test this init_state will actually
        # modify state in-place

        # Validate security analyzer configuration once during initialization
        if self._add_security_risk_prediction and isinstance(
            state.confirmation_policy, NeverConfirm
        ):
            # If security analyzer is enabled, we always need a policy that is not
            # NeverConfirm, otherwise we are just predicting risks without using them,
            # and waste tokens!
            logger.warning(
                "LLM security analyzer is enabled but confirmation "
                "policy is set to NeverConfirm"
            )

        # Configure bash tools with env provider
        self._configure_bash_tools_env_provider(state)

        llm_convertible_messages = [
            event for event in state.events if isinstance(event, LLMConvertibleEvent)
        ]
        if len(llm_convertible_messages) == 0:
            # Prepare system message
            event = SystemPromptEvent(
                source="agent",
                system_prompt=TextContent(text=self.system_message),
                tools=[
                    t.to_openai_tool(
                        add_security_risk_prediction=self._add_security_risk_prediction
                    )
                    for t in self.tools_map.values()
                ],
            )
            on_event(event)

    def _execute_actions(
        self,
        state: ConversationState,
        action_events: list[ActionEvent],
        on_event: ConversationCallbackType,
    ):
        for action_event in action_events:
            self._execute_action_event(state, action_event, on_event=on_event)

    def step(
        self,
        state: ConversationState,
        on_event: ConversationCallbackType,
    ) -> None:
        # Check for pending actions (implicit confirmation)
        # and execute them before sampling new actions.
        pending_actions = ConversationState.get_unmatched_actions(state.events)
        if pending_actions:
            logger.info(
                "Confirmation mode: Executing %d pending action(s)",
                len(pending_actions),
            )
            self._execute_actions(state, pending_actions, on_event)
            return

        # If a condenser is registered with the agent, we need to give it an
        # opportunity to transform the events. This will either produce a list
        # of events, exactly as expected, or a new condensation that needs to be
        # processed before the agent can sample another action.
        if self.condenser is not None:
            view = View.from_events(state.events)
            condensation_result = self.condenser.condense(view)

            match condensation_result:
                case View():
                    llm_convertible_events = condensation_result.events

                case Condensation():
                    on_event(condensation_result)
                    return None

        else:
            llm_convertible_events = [
                e for e in state.events if isinstance(e, LLMConvertibleEvent)
            ]

        # Get LLM Response (Action)
        _messages = LLMConvertibleEvent.events_to_messages(llm_convertible_events)
        logger.debug(
            "Sending messages to LLM: "
            f"{json.dumps([m.model_dump() for m in _messages[1:]], indent=2)}"
        )

        try:
            if self.llm.uses_responses_api():
                llm_response = self.llm.responses(
                    messages=_messages,
                    tools=list(self.tools_map.values()),
                    include=None,
                    store=False,
                    add_security_risk_prediction=self._add_security_risk_prediction,
                    metadata=self.llm.metadata,
                )
            else:
                llm_response = self.llm.completion(
                    messages=_messages,
                    tools=list(self.tools_map.values()),
                    extra_body={"metadata": self.llm.metadata},
                    add_security_risk_prediction=self._add_security_risk_prediction,
                )
        except Exception as e:
            # If there is a condenser registered and the exception is a context window
            # exceeded, we can recover by triggering a condensation request.
            if (
                self.condenser is not None
                and self.condenser.handles_condensation_requests()
                and self.llm.is_context_window_exceeded_exception(e)
            ):
                logger.warning(
                    "LLM raised context window exceeded error, triggering condensation"
                )
                on_event(CondensationRequest())
                return

            # If the error isn't recoverable, keep propagating it up the stack.
            else:
                raise e

        # LLMResponse already contains the converted message and metrics snapshot
        message: Message = llm_response.message

        if message.tool_calls and len(message.tool_calls) > 0:
            if not all(isinstance(c, TextContent) for c in message.content):
                logger.warning(
                    "LLM returned tool calls but message content is not all "
                    "TextContent - ignoring non-text content"
                )

            # Generate unique batch ID for this LLM response
            thought_content = [c for c in message.content if isinstance(c, TextContent)]

            action_events: list[ActionEvent] = []
            for i, tool_call in enumerate(message.tool_calls):
                action_event = self._get_action_event(
                    tool_call,
                    llm_response_id=llm_response.id,
                    on_event=on_event,
                    thought=thought_content
                    if i == 0
                    else [],  # Only first gets thought
                    # Only first gets reasoning content
                    reasoning_content=message.reasoning_content if i == 0 else None,
                    # Only first gets thinking blocks
                    thinking_blocks=list(message.thinking_blocks) if i == 0 else [],
                    responses_reasoning_item=message.responses_reasoning_item
                    if i == 0
                    else None,
                )
                if action_event is None:
                    continue
                action_events.append(action_event)

            # Handle confirmation mode - exit early if actions need confirmation
            if self._requires_user_confirmation(state, action_events):
                return

            if action_events:
                self._execute_actions(state, action_events, on_event)

        else:
            logger.info("LLM produced a message response - awaits user input")
            state.agent_status = AgentExecutionStatus.FINISHED
            msg_event = MessageEvent(
                source="agent",
                llm_message=message,
            )
            on_event(msg_event)

    def _requires_user_confirmation(
        self, state: ConversationState, action_events: list[ActionEvent]
    ) -> bool:
        """
        Decide whether user confirmation is needed to proceed.

        Rules:
            1. Confirmation mode is enabled
            2. Every action requires confirmation
            3. A single `FinishAction` never requires confirmation
            4. A single `ThinkAction` never requires confirmation
        """
        # A single `FinishAction` or `ThinkAction` never requires confirmation
        if len(action_events) == 1 and isinstance(
            action_events[0].action, (FinishAction, ThinkAction)
        ):
            return False

        # If there are no actions there is nothing to confirm
        if len(action_events) == 0:
            return False

        # If a security analyzer is registered, use it to grab the risks of the actions
        # involved. If not, we'll set the risks to UNKNOWN.
        if self.security_analyzer is not None:
            risks = [
                risk
                for _, risk in self.security_analyzer.analyze_pending_actions(
                    action_events
                )
            ]
        else:
            risks = [risk.SecurityRisk.UNKNOWN] * len(action_events)

        # Grab the confirmation policy from the state and pass in the risks.
        if any(state.confirmation_policy.should_confirm(risk) for risk in risks):
            state.agent_status = AgentExecutionStatus.WAITING_FOR_CONFIRMATION
            return True

        return False

    def _get_action_event(
        self,
        tool_call: MessageToolCall,
        llm_response_id: str,
        on_event: ConversationCallbackType,
        thought: list[TextContent] = [],
        reasoning_content: str | None = None,
        thinking_blocks: list[ThinkingBlock | RedactedThinkingBlock] = [],
        responses_reasoning_item: ReasoningItemModel | None = None,
    ) -> ActionEvent | None:
        """Converts a tool call into an ActionEvent, validating arguments.

        NOTE: state will be mutated in-place.
        """
        tool_name = tool_call.name
        tool = self.tools_map.get(tool_name, None)
        # Handle non-existing tools
        if tool is None:
            available = list(self.tools_map.keys())
            err = f"Tool '{tool_name}' not found. Available: {available}"
            logger.error(err)
            # Persist assistant function_call so next turn has matching call_id
            tc_event = ActionEvent(
                source="agent",
                thought=thought,
                reasoning_content=reasoning_content,
                thinking_blocks=thinking_blocks,
                responses_reasoning_item=responses_reasoning_item,
                tool_call=tool_call,
                tool_name=tool_call.name,
                tool_call_id=tool_call.id,
                llm_response_id=llm_response_id,
                action=None,
            )
            on_event(tc_event)
            event = AgentErrorEvent(
                error=err,
                tool_name=tool_name,
                tool_call_id=tool_call.id,
            )
            on_event(event)
            return

        # Validate arguments
        security_risk: risk.SecurityRisk = risk.SecurityRisk.UNKNOWN
        try:
            arguments = json.loads(tool_call.arguments)

            # if the tool has a security_risk field (when security analyzer is set),
            # pop it out as it's not part of the tool's action schema
            if (
                _predicted_risk := arguments.pop("security_risk", None)
            ) is not None and self.security_analyzer is not None:
                try:
                    security_risk = risk.SecurityRisk(_predicted_risk)
                except ValueError:
                    logger.warning(
                        f"Invalid security_risk value from LLM: {_predicted_risk}"
                    )

            assert "security_risk" not in arguments, (
                "Unexpected 'security_risk' key found in tool arguments"
            )
            action: Action = tool.action_from_arguments(arguments)
        except (json.JSONDecodeError, ValidationError) as e:
            err = (
                f"Error validating args {tool_call.arguments} for tool "
                f"'{tool.name}': {e}"
            )
            # Persist assistant function_call so next turn has matching call_id
            tc_event = ActionEvent(
                source="agent",
                thought=thought,
                reasoning_content=reasoning_content,
                thinking_blocks=thinking_blocks,
                responses_reasoning_item=responses_reasoning_item,
                tool_call=tool_call,
                tool_name=tool_call.name,
                tool_call_id=tool_call.id,
                llm_response_id=llm_response_id,
                action=None,
            )
            on_event(tc_event)
            event = AgentErrorEvent(
                error=err,
                tool_name=tool_name,
                tool_call_id=tool_call.id,
            )
            on_event(event)
            return

        action_event = ActionEvent(
            action=action,
            thought=thought,
            reasoning_content=reasoning_content,
            thinking_blocks=thinking_blocks,
            responses_reasoning_item=responses_reasoning_item,
            tool_name=tool.name,
            tool_call_id=tool_call.id,
            tool_call=tool_call,
            llm_response_id=llm_response_id,
            security_risk=security_risk,
        )
        on_event(action_event)
        return action_event

    def _execute_action_event(
        self,
        state: ConversationState,
        action_event: ActionEvent,
        on_event: ConversationCallbackType,
    ):
        """Execute an action event and update the conversation state.

        It will call the tool's executor and update the state & call callback fn
        with the observation.
        """
        tool = self.tools_map.get(action_event.tool_name, None)
        if tool is None:
            raise RuntimeError(
                f"Tool '{action_event.tool_name}' not found. This should not happen "
                "as it was checked earlier."
            )

        # Execute actions!
        observation: Observation = tool(action_event.action)
        assert isinstance(observation, Observation), (
            f"Tool '{tool.name}' executor must return an Observation"
        )

        obs_event = ObservationEvent(
            observation=observation,
            action_id=action_event.id,
            tool_name=tool.name,
            tool_call_id=action_event.tool_call.id,
        )
        on_event(obs_event)

        # Set conversation state
        if tool.name == FinishTool.name:
            state.agent_status = AgentExecutionStatus.FINISHED
        return obs_event
