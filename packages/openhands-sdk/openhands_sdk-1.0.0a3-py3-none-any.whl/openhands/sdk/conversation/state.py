# state.py
import json
from collections.abc import Sequence
from enum import Enum
from typing import TYPE_CHECKING, Any, Self

from pydantic import Field, PrivateAttr

from openhands.sdk.agent.base import AgentBase
from openhands.sdk.conversation.conversation_stats import ConversationStats
from openhands.sdk.conversation.event_store import EventLog
from openhands.sdk.conversation.fifo_lock import FIFOLock
from openhands.sdk.conversation.persistence_const import BASE_STATE, EVENTS_DIR
from openhands.sdk.conversation.secrets_manager import SecretsManager
from openhands.sdk.conversation.types import ConversationCallbackType, ConversationID
from openhands.sdk.event import ActionEvent, ObservationEvent, UserRejectObservation
from openhands.sdk.event.base import Event
from openhands.sdk.io import FileStore, InMemoryFileStore, LocalFileStore
from openhands.sdk.logger import get_logger
from openhands.sdk.security.confirmation_policy import (
    ConfirmationPolicyBase,
    NeverConfirm,
)
from openhands.sdk.utils.models import OpenHandsModel
from openhands.sdk.workspace.base import BaseWorkspace


logger = get_logger(__name__)


class AgentExecutionStatus(str, Enum):
    """Enum representing the current execution state of the agent."""

    IDLE = "idle"  # Agent is ready to receive tasks
    RUNNING = "running"  # Agent is actively processing
    PAUSED = "paused"  # Agent execution is paused by user
    WAITING_FOR_CONFIRMATION = (
        "waiting_for_confirmation"  # Agent is waiting for user confirmation
    )
    FINISHED = "finished"  # Agent has completed the current task
    ERROR = "error"  # Agent encountered an error (optional for future use)
    STUCK = "stuck"  # Agent is stuck in a loop or unable to proceed


if TYPE_CHECKING:
    from openhands.sdk.conversation.secrets_manager import SecretsManager


class ConversationState(OpenHandsModel):
    # ===== Public, validated fields =====
    id: ConversationID = Field(description="Unique conversation ID")

    agent: AgentBase = Field(
        ...,
        description=(
            "The agent running in the conversation. "
            "This is persisted to allow resuming conversations and "
            "check agent configuration to handle e.g., tool changes, "
            "LLM changes, etc."
        ),
    )
    workspace: BaseWorkspace = Field(
        ...,
        description="Working directory for agent operations and tool execution",
    )
    persistence_dir: str | None = Field(
        default="workspace/conversations",
        description="Directory for persisting conversation state and events. "
        "If None, conversation will not be persisted.",
    )

    max_iterations: int = Field(
        default=500,
        gt=0,
        description="Maximum number of iterations the agent can "
        "perform in a single run.",
    )
    stuck_detection: bool = Field(
        default=True,
        description="Whether to enable stuck detection for the agent.",
    )

    # Enum-based state management
    agent_status: AgentExecutionStatus = Field(default=AgentExecutionStatus.IDLE)
    confirmation_policy: ConfirmationPolicyBase = NeverConfirm()

    activated_knowledge_microagents: list[str] = Field(
        default_factory=list,
        description="List of activated knowledge microagents name",
    )

    # Conversation statistics for LLM usage tracking
    stats: ConversationStats = Field(
        default_factory=ConversationStats,
        description="Conversation statistics for tracking LLM metrics",
    )

    # ===== Private attrs (NOT Fields) =====
    _secrets_manager: "SecretsManager" = PrivateAttr(default_factory=SecretsManager)
    _fs: FileStore = PrivateAttr()  # filestore for persistence
    _events: EventLog = PrivateAttr()  # now the storage for events
    _autosave_enabled: bool = PrivateAttr(
        default=False
    )  # to avoid recursion during init
    _on_state_change: ConversationCallbackType | None = PrivateAttr(
        default=None
    )  # callback for state changes
    _lock: FIFOLock = PrivateAttr(
        default_factory=FIFOLock
    )  # FIFO lock for thread safety

    # ===== Public "events" facade (Sequence[Event]) =====
    @property
    def events(self) -> EventLog:
        return self._events

    @property
    def secrets_manager(self) -> SecretsManager:
        """Public accessor for the SecretsManager (stored as a private attr)."""
        return self._secrets_manager

    def set_on_state_change(self, callback: ConversationCallbackType | None) -> None:
        """Set a callback to be called when state changes.

        Args:
            callback: A function that takes an Event (ConversationStateUpdateEvent)
                     or None to remove the callback
        """
        self._on_state_change = callback

    # ===== Base snapshot helpers (same FileStore usage you had) =====
    def _save_base_state(self, fs: FileStore) -> None:
        """
        Persist base state snapshot (no events; events are file-backed).
        """
        payload = self.model_dump_json(exclude_none=True)
        fs.write(BASE_STATE, payload)

    # ===== Factory: open-or-create (no load/save methods needed) =====
    @classmethod
    def create(
        cls: type["ConversationState"],
        id: ConversationID,
        agent: AgentBase,
        workspace: BaseWorkspace,
        persistence_dir: str | None = None,
        max_iterations: int = 500,
        stuck_detection: bool = True,
    ) -> "ConversationState":
        """
        If base_state.json exists: resume (attach EventLog,
            reconcile agent, enforce id).
        Else: create fresh (agent required), persist base, and return.
        """
        file_store = (
            LocalFileStore(persistence_dir) if persistence_dir else InMemoryFileStore()
        )

        try:
            base_text = file_store.read(BASE_STATE)
        except FileNotFoundError:
            base_text = None

        # ---- Resume path ----
        if base_text:
            state = cls.model_validate(json.loads(base_text))

            # Enforce conversation id match
            if state.id != id:
                raise ValueError(
                    f"Conversation ID mismatch: provided {id}, "
                    f"but persisted state has {state.id}"
                )

            # Reconcile agent config with deserialized one
            resolved = agent.resolve_diff_from_deserialized(state.agent)

            # Attach runtime handles and commit reconciled agent (may autosave)
            state._fs = file_store
            state._events = EventLog(file_store, dir_path=EVENTS_DIR)
            state._autosave_enabled = True
            state.agent = resolved

            state.stats = ConversationStats()

            logger.info(
                f"Resumed conversation {state.id} from persistent storage.\n"
                f"State: {state.model_dump(exclude={'agent'})}\n"
                f"Agent: {state.agent.model_dump_succint()}"
            )
            return state

        # ---- Fresh path ----
        if agent is None:
            raise ValueError(
                "agent is required when initializing a new ConversationState"
            )

        state = cls(
            id=id,
            agent=agent,
            workspace=workspace,
            persistence_dir=persistence_dir,
            max_iterations=max_iterations,
            stuck_detection=stuck_detection,
        )
        state._fs = file_store
        state._events = EventLog(file_store, dir_path=EVENTS_DIR)
        state.stats = ConversationStats()

        state._save_base_state(file_store)  # initial snapshot
        state._autosave_enabled = True
        logger.info(
            f"Created new conversation {state.id}\n"
            f"State: {state.model_dump(exclude={'agent'})}\n"
            f"Agent: {state.agent.model_dump_succint()}"
        )
        return state

    # ===== Auto-persist base on public field changes =====
    def __setattr__(self, name, value):
        # Only autosave when:
        # - autosave is enabled (set post-init)
        # - the attribute is a *public field* (not a PrivateAttr)
        # - we have a filestore to write to
        _sentinel = object()
        old = getattr(self, name, _sentinel)
        super().__setattr__(name, value)

        is_field = name in self.__class__.model_fields
        autosave_enabled = getattr(self, "_autosave_enabled", False)
        fs = getattr(self, "_fs", None)

        if not (autosave_enabled and is_field and fs is not None):
            return

        if old is _sentinel or old != value:
            try:
                self._save_base_state(fs)
            except Exception as e:
                logger.exception("Auto-persist base_state failed", exc_info=True)
                raise e

            # Call state change callback if set
            callback = getattr(self, "_on_state_change", None)
            if callback is not None and old is not _sentinel:
                try:
                    # Import here to avoid circular imports
                    from openhands.sdk.event.conversation_state import (
                        ConversationStateUpdateEvent,
                    )

                    # Create a ConversationStateUpdateEvent with the changed field
                    state_update_event = ConversationStateUpdateEvent(
                        key=name, value=value
                    )
                    callback(state_update_event)
                except Exception:
                    logger.exception(
                        f"State change callback failed for field {name}", exc_info=True
                    )

    @staticmethod
    def get_unmatched_actions(events: Sequence[Event]) -> list[ActionEvent]:
        """Find actions in the event history that don't have matching observations.

        This method identifies ActionEvents that don't have corresponding
        ObservationEvents or UserRejectObservations, which typically indicates
        actions that are pending confirmation or execution.

        Args:
            events: List of events to search through

        Returns:
            List of ActionEvent objects that don't have corresponding observations,
            in chronological order
        """
        observed_action_ids = set()
        unmatched_actions = []
        # Search in reverse - recent events are more likely to be unmatched
        for event in reversed(events):
            if isinstance(event, (ObservationEvent, UserRejectObservation)):
                observed_action_ids.add(event.action_id)
            elif isinstance(event, ActionEvent):
                # Only executable actions (validated) are considered pending
                if event.action is not None and event.id not in observed_action_ids:
                    # Insert at beginning to maintain chronological order in result
                    unmatched_actions.insert(0, event)

        return unmatched_actions

    # ===== FIFOLock delegation methods =====
    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Acquire the lock.

        Args:
            blocking: If True, block until lock is acquired. If False, return
                     immediately.
            timeout: Maximum time to wait for lock (ignored if blocking=False).
                    -1 means wait indefinitely.

        Returns:
            True if lock was acquired, False otherwise.
        """
        return self._lock.acquire(blocking=blocking, timeout=timeout)

    def release(self) -> None:
        """
        Release the lock.

        Raises:
            RuntimeError: If the current thread doesn't own the lock.
        """
        self._lock.release()

    def __enter__(self: Self) -> Self:
        """Context manager entry."""
        self._lock.acquire()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self._lock.release()

    def locked(self) -> bool:
        """
        Return True if the lock is currently held by any thread.
        """
        return self._lock.locked()

    def owned(self) -> bool:
        """
        Return True if the lock is currently held by the calling thread.
        """
        return self._lock.owned()
