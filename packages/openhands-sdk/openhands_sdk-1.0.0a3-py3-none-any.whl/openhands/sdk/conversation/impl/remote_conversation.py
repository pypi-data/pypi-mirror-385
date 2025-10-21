import asyncio
import json
import threading
import uuid
from collections.abc import Mapping
from typing import SupportsIndex, overload
from urllib.parse import urlparse

import httpx
import websockets

from openhands.sdk.agent.base import AgentBase
from openhands.sdk.conversation.base import BaseConversation, ConversationStateProtocol
from openhands.sdk.conversation.conversation_stats import ConversationStats
from openhands.sdk.conversation.events_list_base import EventsListBase
from openhands.sdk.conversation.exceptions import ConversationRunError
from openhands.sdk.conversation.secrets_manager import SecretValue
from openhands.sdk.conversation.state import AgentExecutionStatus
from openhands.sdk.conversation.types import ConversationCallbackType, ConversationID
from openhands.sdk.conversation.visualizer import (
    ConversationVisualizer,
    create_default_visualizer,
)
from openhands.sdk.event.base import Event
from openhands.sdk.event.conversation_state import (
    FULL_STATE_KEY,
    ConversationStateUpdateEvent,
)
from openhands.sdk.llm import LLM, Message, TextContent
from openhands.sdk.logger import get_logger
from openhands.sdk.security.confirmation_policy import (
    ConfirmationPolicyBase,
)
from openhands.sdk.workspace import LocalWorkspace, RemoteWorkspace


logger = get_logger(__name__)


def _send_request(
    client: httpx.Client,
    method: str,
    url: str,
    acceptable_status_codes: set[int] | None = None,
    **kwargs,
) -> httpx.Response:
    try:
        response = client.request(method, url, **kwargs)
        if acceptable_status_codes and response.status_code in acceptable_status_codes:
            return response
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        content = None
        try:
            content = e.response.json()
        except Exception:
            content = e.response.text
        logger.error(
            "HTTP request failed (%d %s): %s",
            e.response.status_code,
            e.response.reason_phrase,
            content,
            exc_info=True,
        )
        raise e
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        raise e


class WebSocketCallbackClient:
    """Minimal WS client: connects, forwards events, retries on error."""

    host: str
    conversation_id: str
    callback: ConversationCallbackType
    api_key: str | None
    _thread: threading.Thread | None
    _stop: threading.Event

    def __init__(
        self,
        host: str,
        conversation_id: str,
        callback: ConversationCallbackType,
        api_key: str | None = None,
    ):
        self.host = host
        self.conversation_id = conversation_id
        self.callback = callback
        self.api_key = api_key
        self._thread = None
        self._stop = threading.Event()

    def start(self) -> None:
        if self._thread:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._thread:
            return
        self._stop.set()
        self._thread.join(timeout=5)
        self._thread = None

    def _run(self) -> None:
        try:
            asyncio.run(self._client_loop())
        except RuntimeError:
            # Fallback in case of an already running loop in rare environments
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._client_loop())
            loop.close()

    async def _client_loop(self) -> None:
        parsed = urlparse(self.host)
        ws_scheme = "wss" if parsed.scheme == "https" else "ws"
        base = f"{ws_scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        ws_url = f"{base}/sockets/events/{self.conversation_id}"

        # Add API key as query parameter if provided
        if self.api_key:
            ws_url += f"?session_api_key={self.api_key}"

        delay = 1.0
        while not self._stop.is_set():
            try:
                async with websockets.connect(ws_url) as ws:
                    delay = 1.0
                    async for message in ws:
                        if self._stop.is_set():
                            break
                        try:
                            event = Event.model_validate(json.loads(message))
                            self.callback(event)
                        except Exception:
                            logger.exception(
                                "ws_event_processing_error", stack_info=True
                            )
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception:
                logger.debug("ws_connect_retry", exc_info=True)
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30.0)


class RemoteEventsList(EventsListBase):
    """A list-like, read-only view of remote conversation events.

    On first access it fetches existing events from the server. Afterwards,
    it relies on the WebSocket stream to incrementally append new events.
    """

    _client: httpx.Client
    _conversation_id: str
    _cached_events: list[Event]
    _cached_event_ids: set[str]
    _lock: threading.RLock

    def __init__(self, client: httpx.Client, conversation_id: str):
        self._client = client
        self._conversation_id = conversation_id
        self._cached_events: list[Event] = []
        self._cached_event_ids: set[str] = set()
        self._lock = threading.RLock()
        # Initial fetch to sync existing events
        self._do_full_sync()

    def _do_full_sync(self) -> None:
        """Perform a full sync with the remote API."""
        logger.debug(f"Performing full sync for conversation {self._conversation_id}")

        events = []
        page_id = None

        while True:
            params = {"limit": 100}
            if page_id:
                params["page_id"] = page_id

            resp = _send_request(
                self._client,
                "GET",
                f"/api/conversations/{self._conversation_id}/events/search",
                params=params,
            )
            data = resp.json()

            events.extend([Event.model_validate(item) for item in data["items"]])

            if not data.get("next_page_id"):
                break
            page_id = data["next_page_id"]

        self._cached_events = events
        self._cached_event_ids.update(e.id for e in events)
        logger.debug(f"Full sync completed, {len(events)} events cached")

    def add_event(self, event: Event) -> None:
        """Add a new event to the local cache (called by WebSocket callback)."""
        with self._lock:
            # Check if event already exists to avoid duplicates
            if event.id not in self._cached_event_ids:
                self._cached_events.append(event)
                self._cached_event_ids.add(event.id)
                logger.debug(f"Added event {event.id} to local cache")

    def append(self, event: Event) -> None:
        """Add a new event to the list (for compatibility with EventLog interface)."""
        self.add_event(event)

    def create_default_callback(self) -> ConversationCallbackType:
        """Create a default callback that adds events to this list."""

        def callback(event: Event) -> None:
            self.add_event(event)

        return callback

    def __len__(self) -> int:
        return len(self._cached_events)

    @overload
    def __getitem__(self, index: int) -> Event: ...

    @overload
    def __getitem__(self, index: slice) -> list[Event]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> Event | list[Event]:
        with self._lock:
            return self._cached_events[index]

    def __iter__(self):
        with self._lock:
            return iter(self._cached_events)


class RemoteState(ConversationStateProtocol):
    """A state-like interface for accessing remote conversation state."""

    _client: httpx.Client
    _conversation_id: str
    _events: RemoteEventsList
    _cached_state: dict | None
    _lock: threading.RLock

    def __init__(self, client: httpx.Client, conversation_id: str):
        self._client = client
        self._conversation_id = conversation_id
        self._events = RemoteEventsList(client, conversation_id)

        # Cache for state information to avoid REST calls
        self._cached_state = None
        self._lock = threading.RLock()

    def _get_conversation_info(self) -> dict:
        """Fetch the latest conversation info from the remote API."""
        with self._lock:
            # Return cached state if available
            if self._cached_state is not None:
                return self._cached_state

            # Fallback to REST API if no cached state
            resp = _send_request(
                self._client, "GET", f"/api/conversations/{self._conversation_id}"
            )
            state = resp.json()
            self._cached_state = state
            return state

    def update_state_from_event(self, event: ConversationStateUpdateEvent) -> None:
        """Update cached state from a ConversationStateUpdateEvent."""
        with self._lock:
            # Handle full state snapshot
            if event.key == FULL_STATE_KEY:
                # Update cached state with the full snapshot
                if self._cached_state is None:
                    self._cached_state = {}
                self._cached_state.update(event.value)
            else:
                # Handle individual field updates
                if self._cached_state is None:
                    self._cached_state = {}
                self._cached_state[event.key] = event.value

    def create_state_update_callback(self) -> ConversationCallbackType:
        """Create a callback that updates state from ConversationStateUpdateEvent."""

        def callback(event: Event) -> None:
            if isinstance(event, ConversationStateUpdateEvent):
                self.update_state_from_event(event)

        return callback

    @property
    def events(self) -> RemoteEventsList:
        """Access to the events list."""
        return self._events

    @property
    def id(self) -> ConversationID:
        """The conversation ID."""
        return uuid.UUID(self._conversation_id)

    @property
    def agent_status(self) -> AgentExecutionStatus:
        """The current agent execution status."""
        info = self._get_conversation_info()
        status_str = info.get("agent_status", None)
        if status_str is None:
            raise RuntimeError(
                "agent_status missing in conversation info: " + str(info)
            )
        return AgentExecutionStatus(status_str)

    @agent_status.setter
    def agent_status(self, value: AgentExecutionStatus) -> None:
        """Set agent status is No-OP for RemoteConversation.

        # For remote conversations, agent status is managed server-side
        # This setter is provided for test compatibility but doesn't actually change remote state  # noqa: E501
        """  # noqa: E501
        raise NotImplementedError(
            f"Setting agent_status on RemoteState has no effect. "
            f"Remote agent status is managed server-side. Attempted to set: {value}"
        )

    @property
    def confirmation_policy(self) -> ConfirmationPolicyBase:
        """The confirmation policy."""
        info = self._get_conversation_info()
        policy_data = info.get("confirmation_policy")
        if policy_data is None:
            raise RuntimeError(
                "confirmation_policy missing in conversation info: " + str(info)
            )
        return ConfirmationPolicyBase.model_validate(policy_data)

    @property
    def activated_knowledge_microagents(self) -> list[str]:
        """List of activated knowledge microagents."""
        info = self._get_conversation_info()
        return info.get("activated_knowledge_microagents", [])

    @property
    def agent(self):
        """The agent configuration (fetched from remote)."""
        info = self._get_conversation_info()
        agent_data = info.get("agent")
        if agent_data is None:
            raise RuntimeError("agent missing in conversation info: " + str(info))
        return AgentBase.model_validate(agent_data)

    @property
    def workspace(self):
        """The working directory (fetched from remote)."""
        info = self._get_conversation_info()
        workspace = info.get("workspace")
        if workspace is None:
            raise RuntimeError("workspace missing in conversation info: " + str(info))
        return workspace

    @property
    def persistence_dir(self):
        """The persistence directory (fetched from remote)."""
        info = self._get_conversation_info()
        persistence_dir = info.get("persistence_dir")
        if persistence_dir is None:
            raise RuntimeError(
                "persistence_dir missing in conversation info: " + str(info)
            )
        return persistence_dir

    def model_dump(self, **_kwargs):
        """Get a dictionary representation of the remote state."""
        info = self._get_conversation_info()
        return info

    def model_dump_json(self, **kwargs):
        """Get a JSON representation of the remote state."""
        return json.dumps(self.model_dump(**kwargs))

    # Context manager methods for compatibility with ConversationState
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class RemoteConversation(BaseConversation):
    _id: uuid.UUID
    _state: "RemoteState"
    _visualizer: ConversationVisualizer | None
    _ws_client: "WebSocketCallbackClient | None"
    agent: AgentBase
    _callbacks: list[ConversationCallbackType]
    max_iteration_per_run: int
    workspace: RemoteWorkspace
    _client: httpx.Client

    def __init__(
        self,
        agent: AgentBase,
        workspace: RemoteWorkspace,
        conversation_id: ConversationID | None = None,
        callbacks: list[ConversationCallbackType] | None = None,
        max_iteration_per_run: int = 500,
        stuck_detection: bool = True,
        visualize: bool = False,
        secrets: Mapping[str, SecretValue] | None = None,
        **_: object,
    ) -> None:
        """Remote conversation proxy that talks to an agent server.

        Args:
            agent: Agent configuration (will be sent to the server)
            host: Base URL of the agent server (e.g., http://localhost:3000)
            workspace: The working directory for agent operations and tool execution.
            api_key: Optional API key for authentication (sent as X-Session-API-Key
                header)
            conversation_id: Optional existing conversation id to attach to
            callbacks: Optional callbacks to receive events (not yet streamed)
            max_iteration_per_run: Max iterations configured on server
            stuck_detection: Whether to enable stuck detection on server
            visualize: Whether to enable the default visualizer callback
        """
        self.agent = agent
        self._callbacks = callbacks or []
        self.max_iteration_per_run = max_iteration_per_run
        self.workspace = workspace
        self._client = workspace.client

        if conversation_id is None:
            payload = {
                "agent": agent.model_dump(
                    mode="json", context={"expose_secrets": True}
                ),
                "initial_message": None,
                "max_iterations": max_iteration_per_run,
                "stuck_detection": stuck_detection,
                # We need to convert RemoteWorkspace to LocalWorkspace for the server
                "workspace": LocalWorkspace(
                    working_dir=self.workspace.working_dir
                ).model_dump(),
            }
            resp = _send_request(
                self._client, "POST", "/api/conversations", json=payload
            )
            data = resp.json()
            # Expect a ConversationInfo
            cid = data.get("id") or data.get("conversation_id")
            if not cid:
                raise RuntimeError(
                    "Invalid response from server: missing conversation id"
                )
            self._id = uuid.UUID(cid)
        else:
            # Attach to existing
            self._id = conversation_id
            # Validate it exists
            _send_request(self._client, "GET", f"/api/conversations/{self._id}")

        # Initialize the remote state
        self._state = RemoteState(self._client, str(self._id))

        # Add default callback to maintain local event state
        default_callback = self._state.events.create_default_callback()
        self._callbacks.append(default_callback)

        # Add callback to update state from websocket events
        state_update_callback = self._state.create_state_update_callback()
        self._callbacks.append(state_update_callback)

        # Add default visualizer callback if requested
        if visualize:
            self._visualizer = create_default_visualizer()
            if self._visualizer is not None:
                self._callbacks.append(self._visualizer.on_event)
        else:
            self._visualizer = None

        # Compose all callbacks into a single callback
        composed_callback = BaseConversation.compose_callbacks(self._callbacks)

        # Initialize WebSocket client for callbacks
        self._ws_client = WebSocketCallbackClient(
            host=self.workspace.host,
            conversation_id=str(self._id),
            callback=composed_callback,
            api_key=self.workspace.api_key,
        )
        self._ws_client.start()

        # Initialize secrets if provided
        if secrets:
            # Convert dict[str, str] to dict[str, SecretValue]
            secret_values: dict[str, SecretValue] = {k: v for k, v in secrets.items()}
            self.update_secrets(secret_values)

    @property
    def id(self) -> ConversationID:
        return self._id

    @property
    def state(self) -> RemoteState:
        """Access to remote conversation state."""
        return self._state

    @property
    def conversation_stats(self) -> ConversationStats:
        """Get conversation stats from remote server."""
        info = self._state._get_conversation_info()
        stats_data = info.get("conversation_stats", {})
        return ConversationStats.model_validate(stats_data)

    @property
    def stuck_detector(self):
        """Stuck detector for compatibility.
        Not implemented for remote conversations."""
        raise NotImplementedError(
            "For remote conversations, stuck detection is not available"
            " since it would be handled server-side."
        )

    def send_message(self, message: str | Message) -> None:
        if isinstance(message, str):
            message = Message(role="user", content=[TextContent(text=message)])
        assert message.role == "user", (
            "Only user messages are allowed to be sent to the agent."
        )
        payload = {
            "role": message.role,
            "content": [c.model_dump() for c in message.content],
            "run": False,  # Mirror local semantics; explicit run() must be called
        }
        _send_request(
            self._client, "POST", f"/api/conversations/{self._id}/events", json=payload
        )

    def run(self) -> None:
        # Trigger a run on the server using the dedicated run endpoint.
        # Let the server tell us if it's already running (409), avoiding an extra GET.
        try:
            resp = _send_request(
                self._client,
                "POST",
                f"/api/conversations/{self._id}/run",
                acceptable_status_codes={200, 201, 204, 409},
                timeout=1800,
            )
        except Exception as e:  # httpx errors already logged by _send_request
            # Surface conversation id to help resuming
            raise ConversationRunError(self._id, e) from e
        if resp.status_code == 409:
            logger.info("Conversation is already running; skipping run trigger")
            return
        logger.info(f"run() triggered successfully: {resp}")

    def set_confirmation_policy(self, policy: ConfirmationPolicyBase) -> None:
        payload = {"policy": policy.model_dump()}
        _send_request(
            self._client,
            "POST",
            f"/api/conversations/{self._id}/confirmation_policy",
            json=payload,
        )

    def reject_pending_actions(self, reason: str = "User rejected the action") -> None:
        # Equivalent to rejecting confirmation: pause
        _send_request(
            self._client,
            "POST",
            f"/api/conversations/{self._id}/events/respond_to_confirmation",
            json={"accept": False, "reason": reason},
        )

    def pause(self) -> None:
        _send_request(self._client, "POST", f"/api/conversations/{self._id}/pause")

    def update_secrets(self, secrets: Mapping[str, SecretValue]) -> None:
        # Convert SecretValue to strings for JSON serialization
        # SecretValue can be str or callable, we need to handle both
        serializable_secrets = {}
        for key, value in secrets.items():
            if callable(value):
                # If it's a callable, call it to get the actual secret
                serializable_secrets[key] = value()
            else:
                # If it's already a string, use it directly
                serializable_secrets[key] = value

        payload = {"secrets": serializable_secrets}
        _send_request(
            self._client, "POST", f"/api/conversations/{self._id}/secrets", json=payload
        )

    def generate_title(self, llm: LLM | None = None, max_length: int = 50) -> str:
        """Generate a title for the conversation based on the first user message.

        Args:
            llm: Optional LLM to use for title generation. If provided, its usage_id
                 will be sent to the server. If not provided, uses the agent's LLM.
            max_length: Maximum length of the generated title.

        Returns:
            A generated title for the conversation.
        """
        # For remote conversations, delegate to the server endpoint
        payload = {
            "max_length": max_length,
            "llm": llm.model_dump(mode="json", context={"expose_secrets": True})
            if llm
            else None,
        }

        resp = _send_request(
            self._client,
            "POST",
            f"/api/conversations/{self._id}/generate_title",
            json=payload,
        )
        data = resp.json()
        return data["title"]

    def close(self) -> None:
        try:
            # Stop WebSocket client if it exists
            if self._ws_client:
                self._ws_client.stop()
                self._ws_client = None
        except Exception:
            pass

        try:
            self._client.close()
        except Exception:
            pass

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
