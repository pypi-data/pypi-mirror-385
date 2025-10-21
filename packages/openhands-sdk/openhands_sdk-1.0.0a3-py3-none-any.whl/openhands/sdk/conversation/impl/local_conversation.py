import uuid
from collections.abc import Mapping
from pathlib import Path

from openhands.sdk.agent.base import AgentBase
from openhands.sdk.conversation.base import BaseConversation
from openhands.sdk.conversation.exceptions import ConversationRunError
from openhands.sdk.conversation.secrets_manager import SecretValue
from openhands.sdk.conversation.state import AgentExecutionStatus, ConversationState
from openhands.sdk.conversation.stuck_detector import StuckDetector
from openhands.sdk.conversation.title_utils import generate_conversation_title
from openhands.sdk.conversation.types import ConversationCallbackType, ConversationID
from openhands.sdk.conversation.visualizer import (
    ConversationVisualizer,
    create_default_visualizer,
)
from openhands.sdk.event import (
    MessageEvent,
    PauseEvent,
    UserRejectObservation,
)
from openhands.sdk.llm import LLM, Message, TextContent
from openhands.sdk.llm.llm_registry import LLMRegistry
from openhands.sdk.logger import get_logger
from openhands.sdk.security.confirmation_policy import (
    ConfirmationPolicyBase,
)
from openhands.sdk.workspace import LocalWorkspace


logger = get_logger(__name__)


class LocalConversation(BaseConversation):
    agent: AgentBase
    workspace: LocalWorkspace
    _state: ConversationState
    _visualizer: ConversationVisualizer | None
    _on_event: ConversationCallbackType
    max_iteration_per_run: int
    _stuck_detector: StuckDetector | None
    llm_registry: LLMRegistry

    def __init__(
        self,
        agent: AgentBase,
        workspace: str | LocalWorkspace,
        persistence_dir: str | None = None,
        conversation_id: ConversationID | None = None,
        callbacks: list[ConversationCallbackType] | None = None,
        max_iteration_per_run: int = 500,
        stuck_detection: bool = True,
        visualize: bool = True,
        secrets: Mapping[str, SecretValue] | None = None,
        **_: object,
    ):
        """Initialize the conversation.

        Args:
            agent: The agent to use for the conversation
            workspace: Working directory for agent operations and tool execution
            persistence_dir: Directory for persisting conversation state and events
            conversation_id: Optional ID for the conversation. If provided, will
                      be used to identify the conversation. The user might want to
                      suffix their persistent filestore with this ID.
            callbacks: Optional list of callback functions to handle events
            max_iteration_per_run: Maximum number of iterations per run
            visualize: Whether to enable default visualization. If True, adds
                      a default visualizer callback. If False, relies on
                      application to provide visualization through callbacks.
            stuck_detection: Whether to enable stuck detection
        """
        self.agent = agent
        if isinstance(workspace, str):
            workspace = LocalWorkspace(working_dir=workspace)
        assert isinstance(workspace, LocalWorkspace), (
            "workspace must be a LocalWorkspace instance"
        )
        self.workspace = workspace
        if not Path(self.workspace.working_dir).exists():
            Path(self.workspace.working_dir).mkdir(parents=True, exist_ok=True)

        # Create-or-resume: factory inspects BASE_STATE to decide
        desired_id = conversation_id or uuid.uuid4()
        self._state = ConversationState.create(
            id=desired_id,
            agent=agent,
            workspace=self.workspace,
            persistence_dir=self.get_persistence_dir(persistence_dir, desired_id)
            if persistence_dir
            else None,
            max_iterations=max_iteration_per_run,
            stuck_detection=stuck_detection,
        )

        # Default callback: persist every event to state
        def _default_callback(e):
            self._state.events.append(e)

        composed_list = (callbacks if callbacks else []) + [_default_callback]
        # Add default visualizer if requested
        if visualize:
            self._visualizer = create_default_visualizer(
                conversation_stats=self._state.stats
            )
            composed_list = [self._visualizer.on_event] + composed_list
            # visualize should happen first for visibility
        else:
            self._visualizer = None

        self._on_event = BaseConversation.compose_callbacks(composed_list)
        self.max_iteration_per_run = max_iteration_per_run

        # Initialize stuck detector
        self._stuck_detector = StuckDetector(self._state) if stuck_detection else None

        with self._state:
            self.agent.init_state(self._state, on_event=self._on_event)

        # Register existing llms in agent
        self.llm_registry = LLMRegistry()
        self.llm_registry.subscribe(self._state.stats.register_llm)
        for llm in list(self.agent.get_all_llms()):
            self.llm_registry.add(llm)

        # Initialize secrets if provided
        if secrets:
            # Convert dict[str, str] to dict[str, SecretValue]
            secret_values: dict[str, SecretValue] = {k: v for k, v in secrets.items()}
            self.update_secrets(secret_values)

    @property
    def id(self) -> ConversationID:
        """Get the unique ID of the conversation."""
        return self._state.id

    @property
    def state(self) -> ConversationState:
        """Get the conversation state.

        It returns a protocol that has a subset of ConversationState methods
        and properties. We will have the ability to access the same properties
        of ConversationState on a remote conversation object.
        But we won't be able to access methods that mutate the state.
        """
        return self._state

    @property
    def conversation_stats(self):
        return self._state.stats

    @property
    def stuck_detector(self) -> StuckDetector | None:
        """Get the stuck detector instance if enabled."""
        return self._stuck_detector

    def send_message(self, message: str | Message) -> None:
        """Send a message to the agent.

        Args:
            message: Either a string (which will be converted to a user message)
                    or a Message object
        """
        # Convert string to Message if needed
        if isinstance(message, str):
            message = Message(role="user", content=[TextContent(text=message)])

        assert message.role == "user", (
            "Only user messages are allowed to be sent to the agent."
        )
        with self._state:
            if self._state.agent_status == AgentExecutionStatus.FINISHED:
                self._state.agent_status = (
                    AgentExecutionStatus.IDLE
                )  # now we have a new message

            # TODO: We should add test cases for all these scenarios
            activated_microagent_names: list[str] = []
            extended_content: list[TextContent] = []

            # Handle per-turn user message (i.e., knowledge agent trigger)
            if self.agent.agent_context:
                ctx = self.agent.agent_context.get_user_message_suffix(
                    user_message=message,
                    # We skip microagents that were already activated
                    skip_microagent_names=self._state.activated_knowledge_microagents,
                )
                # TODO(calvin): we need to update
                # self._state.activated_knowledge_microagents
                # so condenser can work
                if ctx:
                    content, activated_microagent_names = ctx
                    logger.debug(
                        f"Got augmented user message content: {content}, "
                        f"activated microagents: {activated_microagent_names}"
                    )
                    extended_content.append(content)
                    self._state.activated_knowledge_microagents.extend(
                        activated_microagent_names
                    )

            user_msg_event = MessageEvent(
                source="user",
                llm_message=message,
                activated_microagents=activated_microagent_names,
                extended_content=extended_content,
            )
            self._on_event(user_msg_event)

    def run(self) -> None:
        """Runs the conversation until the agent finishes.

        In confirmation mode:
        - First call: creates actions but doesn't execute them, stops and waits
        - Second call: executes pending actions (implicit confirmation)

        In normal mode:
        - Creates and executes actions immediately

        Can be paused between steps
        """

        with self._state:
            if self._state.agent_status == AgentExecutionStatus.PAUSED:
                self._state.agent_status = AgentExecutionStatus.RUNNING

        iteration = 0
        try:
            while True:
                logger.debug(f"Conversation run iteration {iteration}")
                with self._state:
                    # Pause attempts to acquire the state lock
                    # Before value can be modified step can be taken
                    # Ensure step conditions are checked when lock is already acquired
                    if self._state.agent_status in [
                        AgentExecutionStatus.FINISHED,
                        AgentExecutionStatus.PAUSED,
                        AgentExecutionStatus.STUCK,
                    ]:
                        break

                    # Check for stuck patterns if enabled
                    if self._stuck_detector:
                        is_stuck = self._stuck_detector.is_stuck()

                        if is_stuck:
                            logger.warning("Stuck pattern detected.")
                            self._state.agent_status = AgentExecutionStatus.STUCK
                            continue

                    # clear the flag before calling agent.step() (user approved)
                    if (
                        self._state.agent_status
                        == AgentExecutionStatus.WAITING_FOR_CONFIRMATION
                    ):
                        self._state.agent_status = AgentExecutionStatus.RUNNING

                    # step must mutate the SAME state object
                    self.agent.step(self._state, on_event=self._on_event)
                    iteration += 1

                    # Check for non-finished terminal conditions
                    # Note: We intentionally do NOT check for FINISHED status here.
                    # This allows concurrent user messages to be processed:
                    # 1. Agent finishes and sets status to FINISHED
                    # 2. User sends message concurrently via send_message()
                    # 3. send_message() waits for FIFO lock, then sets status to IDLE
                    # 4. Run loop continues to next iteration and processes the message
                    # 5. Without this design, concurrent messages would be lost
                    if (
                        self.state.agent_status
                        == AgentExecutionStatus.WAITING_FOR_CONFIRMATION
                        or iteration >= self.max_iteration_per_run
                    ):
                        break
        except Exception as e:
            # Re-raise with conversation id for better UX; include original traceback
            raise ConversationRunError(self._state.id, e) from e

    def set_confirmation_policy(self, policy: ConfirmationPolicyBase) -> None:
        """Set the confirmation policy and store it in conversation state."""
        with self._state:
            self._state.confirmation_policy = policy
        logger.info(f"Confirmation policy set to: {policy}")

    def reject_pending_actions(self, reason: str = "User rejected the action") -> None:
        """Reject all pending actions from the agent.

        This is a non-invasive method to reject actions between run() calls.
        Also clears the agent_waiting_for_confirmation flag.
        """
        pending_actions = ConversationState.get_unmatched_actions(self._state.events)

        with self._state:
            # Always clear the agent_waiting_for_confirmation flag
            if (
                self._state.agent_status
                == AgentExecutionStatus.WAITING_FOR_CONFIRMATION
            ):
                self._state.agent_status = AgentExecutionStatus.IDLE

            if not pending_actions:
                logger.warning("No pending actions to reject")
                return

            for action_event in pending_actions:
                # Create rejection observation
                rejection_event = UserRejectObservation(
                    action_id=action_event.id,
                    tool_name=action_event.tool_name,
                    tool_call_id=action_event.tool_call_id,
                    rejection_reason=reason,
                )
                self._on_event(rejection_event)
                logger.info(f"Rejected pending action: {action_event} - {reason}")

    def pause(self) -> None:
        """Pause agent execution.

        This method can be called from any thread to request that the agent
        pause execution. The pause will take effect at the next iteration
        of the run loop (between agent steps).

        Note: If called during an LLM completion, the pause will not take
        effect until the current LLM call completes.
        """

        if self._state.agent_status == AgentExecutionStatus.PAUSED:
            return

        with self._state:
            # Only pause when running or idle
            if (
                self._state.agent_status == AgentExecutionStatus.IDLE
                or self._state.agent_status == AgentExecutionStatus.RUNNING
            ):
                self._state.agent_status = AgentExecutionStatus.PAUSED
                pause_event = PauseEvent()
                self._on_event(pause_event)
                logger.info("Agent execution pause requested")

    def update_secrets(self, secrets: Mapping[str, SecretValue]) -> None:
        """Add secrets to the conversation.

        Args:
            secrets: Dictionary mapping secret keys to values or no-arg callables.
                     SecretValue = str | Callable[[], str]. Callables are invoked lazily
                     when a command references the secret key.
        """

        secrets_manager = self._state.secrets_manager
        secrets_manager.update_secrets(secrets)
        logger.info(f"Added {len(secrets)} secrets to conversation")

    def close(self) -> None:
        """Close the conversation and clean up all tool executors."""
        logger.debug("Closing conversation and cleaning up tool executors")
        for tool in self.agent.tools_map.values():
            try:
                executable_tool = tool.as_executable()
                executable_tool.executor.close()
            except NotImplementedError:
                # Tool has no executor, skip it
                continue
            except Exception as e:
                logger.warning(f"Error closing executor for tool '{tool.name}': {e}")

    def generate_title(self, llm: LLM | None = None, max_length: int = 50) -> str:
        """Generate a title for the conversation based on the first user message.

        Args:
            llm: Optional LLM to use for title generation. If not provided,
                 uses self.agent.llm.
            max_length: Maximum length of the generated title.

        Returns:
            A generated title for the conversation.

        Raises:
            ValueError: If no user messages are found in the conversation.
        """
        # Use provided LLM or fall back to agent's LLM
        llm_to_use = llm or self.agent.llm

        return generate_conversation_title(
            events=self._state.events, llm=llm_to_use, max_length=max_length
        )

    def __del__(self) -> None:
        """Ensure cleanup happens when conversation is destroyed."""
        try:
            self.close()
        except Exception as e:
            logger.warning(f"Error during conversation cleanup: {e}", exc_info=True)
