import asyncio
import re
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Generic,
    Optional,
    TypeVar,
    get_args,
    get_origin,
    AsyncContextManager,
)
from types import TracebackType

from pydantic import BaseModel, PrivateAttr
from naylence.fame.core import (
    AGENT_CAPABILITY,
    DataFrame,
    DeliveryAckFrame,
    FameAddress,
    FameDeliveryContext,
    FameEnvelope,
    FameFabric,
    FameMessageResponse,
    create_fame_envelope,
    generate_id,
)
from naylence.fame.util import logging
from naylence.fame.util.util import camel_to_snake_case
from naylence.agent.a2a_types import (
    AgentCard,
    AuthenticationInfo,
    DataPart,
    Task,
    TaskArtifactUpdateEvent,
    TaskIdParams,
    TaskPushNotificationConfig,
    TaskQueryParams,
    TaskSendParams,
    TaskState,
    TaskStatusUpdateEvent,
    TextPart,
)
from naylence.agent.agent import Agent
from naylence.agent.errors import (
    PushNotificationNotSupportedException,
    TaskNotCancelableException,
    UnsupportedOperationException,
)
from naylence.agent.rpc_adapter import handle_agent_rpc_request
from naylence.agent.util import decode_fame_data_payload, make_task
from naylence.fame.storage.storage_provider import (
    StorageProvider,
)

logger = logging.getLogger(__name__)


TERMINAL_TASK_STATES = {
    TaskState.COMPLETED,
    TaskState.CANCELED,
    TaskState.FAILED,
}


class BaseAgentState(BaseModel):
    # Internal fields for context manager functionality
    _agent: Optional["BaseAgent"] = PrivateAttr(default=None)
    _lock_acquired: bool = PrivateAttr(default=False)
    _loaded_state: Optional["BaseAgentState"] = PrivateAttr(default=None)

    model_config = {"extra": "forbid"}

    def _set_agent(self, agent: "BaseAgent") -> None:
        """Internal method to set the agent reference."""
        self._agent = agent

    async def __aenter__(self):
        """Load fresh state and acquire lock."""
        if self._agent is None:
            raise RuntimeError("State is not associated with an agent")

        # Acquire the agent's state lock
        await self._agent._state_lock.acquire()
        self._lock_acquired = True

        try:
            # Load fresh state from storage
            loaded_state = await self._agent._load_state()
            # Keep reference to the loaded state for saving later
            self._loaded_state = loaded_state
            return loaded_state
        except Exception:
            self._agent._state_lock.release()
            self._lock_acquired = False
            raise

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Save state and release lock."""
        try:
            if (
                exc_type is None
                and self._agent is not None
                and self._loaded_state is not None
            ):
                # Save the loaded state instance that was modified
                await self._agent._save_state(self._loaded_state)
        finally:
            if self._lock_acquired and self._agent is not None:
                self._agent._state_lock.release()
                self._lock_acquired = False


StateT = TypeVar("StateT", bound=BaseAgentState)


class BaseAgent(Agent, Generic[StateT]):
    # Optional class-level way to declare the state model for the agent
    STATE_MODEL: type[BaseModel] | None = None

    def __init__(
        self,
        name: str | None = None,
        *,
        state_model: type[BaseModel] | None = None,
        state_namespace: str | None = None,
        state_key: str = "state",
        state_factory=None,
    ):
        self._name = name or camel_to_snake_case(self.__class__.__name__)
        self._address = None
        self._capabilities = [AGENT_CAPABILITY]
        self._subscriptions: dict[str, asyncio.Task] = {}  # id → Task
        self._storage_provider: Optional[StorageProvider] = None

        # --- Simple persisted state (optional) -------------------------
        # Extract state type from Generic parameter if available
        self._state_model: type[BaseModel] | None = (
            state_model
            or getattr(self, "STATE_MODEL", None)
            or self._extract_state_type_from_generic()
        )
        self._state_namespace_raw: Optional[str] = state_namespace
        self._state_key: str = state_key
        self._state_factory = state_factory  # Callable that creates default state
        self._state_store = None  # lazy; kv-store handle
        self._state_cache: Optional[StateT] = None
        self._state_lock = asyncio.Lock()  # Protect state operations
        # ----------------------------------------------------------------

    def _extract_state_type_from_generic(self) -> type[BaseModel] | None:
        """Extract the StateT type from Generic[StateT] if specified."""
        # Look through the class hierarchy for Generic base
        for base in getattr(self.__class__, "__orig_bases__", []):
            origin = get_origin(base)
            if origin is not None and issubclass(origin, BaseAgent):
                args = get_args(base)
                if args and len(args) > 0:
                    state_type = args[0]
                    # Ensure it's a BaseModel subclass
                    if isinstance(state_type, type) and issubclass(
                        state_type, BaseModel
                    ):
                        return state_type
        return None

    @property
    def capabilities(self):
        return self._capabilities

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def spec(self) -> Dict:
        return {"address": self._address}

    @property
    def address(self) -> Optional[FameAddress]:
        return self._address

    @address.setter
    def address(self, address: FameAddress):
        self._address = address

    @property
    def storage_provider(self) -> Optional[StorageProvider]:
        if not self._storage_provider:
            from naylence.fame.node.node import get_node

            node = get_node()
            self._storage_provider = node.storage_provider

        return self._storage_provider

    # ---------------------- Persisted state helpers ----------------------
    def _sanitize_namespace(self, ns: str) -> str:
        """
        Produce a filesystem/SQLite-friendly name.
        Allows [A-Za-z0-9._-], replaces others with '_', trims/limits length.
        """
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", ns)
        safe = safe.strip("._-")
        if not safe:
            safe = "ns"
        # keep it reasonably short for filenames
        return safe[:120]

    def _default_state_namespace(self) -> str:
        if not self._name:
            raise RuntimeError(
                "Cannot derive default state namespace without agent name. "
                "Set 'name' or provide 'state_namespace'."
            )
        return f"__agent_{self.name}"

    async def _ensure_state_store(self, model_type: type[BaseModel]) -> None:
        if self._state_store is None:
            assert self.storage_provider is not None, (
                "Storage provider is not available"
            )
            namespace = self._state_namespace_raw or self._default_state_namespace()
            self._state_store = await self.storage_provider.get_kv_store(
                model_type, namespace=namespace
            )

    async def _load_state(self) -> StateT:
        """Load state from storage, initialize if not found."""
        if self._state_cache is not None:
            return self._state_cache

        if self._state_model is None:
            raise RuntimeError(
                "No state model configured. Provide via Generic[StateT], STATE_MODEL, "
                "constructor 'state_model=', or 'state_factory='."
            )

        await self._ensure_state_store(self._state_model)
        state = await self._state_store.get(self._state_key)  # type: ignore[attr-defined]

        if state is None:
            # Initialize new state
            if self._state_factory is not None:
                state = self._state_factory()
            else:
                state = self._state_model()
            await self._state_store.set(self._state_key, state)  # type: ignore[attr-defined]

        self._state_cache = state  # type: ignore[assignment]
        # Set agent reference for context manager functionality
        if hasattr(state, "_set_agent"):
            state._set_agent(self)  # type: ignore[attr-defined]
        return state  # type: ignore[return-value]

    async def _save_state(self, state: StateT) -> None:
        """Save state to storage."""
        model_type = type(state)
        await self._ensure_state_store(model_type)
        await self._state_store.set(self._state_key, state)  # type: ignore[attr-defined]
        self._state_cache = state

    @property
    def state(self) -> AsyncContextManager[StateT]:
        """
        Returns an async context manager for the state object.
        Usage:
            async with agent.state as s:
                s.count += 1
                # Auto-saves on context exit
        """
        if self._state_model is None:
            raise RuntimeError("No state model configured")

        # Create a state instance for context manager use
        state_instance = self._state_model()
        state_instance._set_agent(self)  # type: ignore[attr-defined]
        return state_instance  # type: ignore[return-value]

    async def get_state(self) -> StateT:
        """Get current state (for direct access without auto-save)."""
        async with self._state_lock:
            return await self._load_state()

    async def clear_state(self) -> None:
        """Clear the persisted state."""
        async with self._state_lock:
            if self._state_store is not None:
                await self._state_store.set(self._state_key, None)  # type: ignore[attr-defined]
            self._state_cache = None

    # ------------------- End persisted state helpers ---------------------

    @staticmethod
    def _is_rpc_request(raw_message: Any):
        return (
            isinstance(raw_message, dict)
            and "jsonrpc" in raw_message
            and "method" in raw_message
            and "params" in raw_message
        )

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise UnsupportedOperationException(
            f"Agent {self} does not support operation '__call__'"
        )

    async def handle_message(
        self, envelope: FameEnvelope, context: Optional[FameDeliveryContext] = None
    ) -> Optional[FameMessageResponse | AsyncIterator[FameMessageResponse]]:
        if isinstance(envelope.frame, DeliveryAckFrame):
            logger.debug("received_delivery_ack", delivery_ack_frame=envelope.frame)
            if envelope.frame.ok:
                logger.trace(
                    "positive_delivery_ack",
                    corr_id=envelope.corr_id,
                )
                return None
            task_id = envelope.corr_id
            if task_id:
                task = self._subscriptions.get(task_id)
                if task and not task.done():
                    logger.info("cancelling_stream_on_nack", task_id=task_id)
                    task.cancel()
            return None
        if not isinstance(envelope.frame, DataFrame):
            raise RuntimeError(
                f"Invalid envelope frame. Expected {DataFrame}, actual: {type(envelope.frame)}"
            )
        decoded_payload = decode_fame_data_payload(envelope.frame)
        if BaseAgent._is_rpc_request(decoded_payload):
            return await self._handle_rpc_message(
                decoded_payload, envelope.reply_to, envelope.trace_id
            )

        return await self.on_message(decoded_payload)

    async def on_message(self, message: Any) -> Optional[FameMessageResponse]:
        """Override to process any *non-RPC* inbound message delivered by the Fabric.

        Examples include push notifications, alerts, or custom application signals. The
        default implementation just logs the payload.
        """
        logger.warning("unhandled_inbound_message", message=message)
        return None  # No response by default

    async def _handle_rpc_message(
        self,
        rpc_request: dict,
        reply_to: Optional[FameAddress] = None,
        trace_id: Optional[str] = None,
    ) -> Optional[FameMessageResponse | AsyncIterator[FameMessageResponse]]:
        # ⏩ For a long‐lived subscribe, stream in the background so we don't block the recv loop
        if rpc_request.get("method") == "tasks/sendSubscribe":
            # spawn the generator+send in its own task and return immediately
            task = asyncio.create_task(
                self._stream_send_subscribe(rpc_request, reply_to)
            )
            id = rpc_request.get("id")
            if id:
                self._subscriptions[id] = task
            return

        # For all other RPCs, return an async generator that wraps each response in FameMessageResponse
        async def _rpc_response_generator():
            response_iter = handle_agent_rpc_request(self, rpc_request)
            async for rpc_response in response_iter:
                reply_to_addr = reply_to or rpc_request["params"].get("reply_to")
                if not reply_to_addr:
                    logger.warning("Missing reply_to in request")
                    break

                frame = DataFrame(payload=rpc_response)
                envelope = create_fame_envelope(
                    frame=frame,
                    to=reply_to_addr,
                    trace_id=trace_id,
                    corr_id=rpc_request.get("id"),
                    # response_type=FameResponseType.ACK # not yet
                )
                yield FameMessageResponse(envelope=envelope)

        return _rpc_response_generator()

    async def _stream_send_subscribe(self, rpc_request, reply_to):
        """
        Drain the subscribe generator without holding up the main recv loop.
        """
        try:
            async for rpc_response in handle_agent_rpc_request(self, rpc_request):
                target = reply_to or rpc_request["params"].get("reply_to")
                if not target:
                    logger.warning("Missing reply_to in sendSubscribe stream")
                    return

                frame = DataFrame(payload=rpc_response)
                env = create_fame_envelope(
                    frame=frame, to=target, corr_id=rpc_request.get("id")
                )
                await FameFabric.current().send(env)
        except asyncio.CancelledError:
            logger.debug("send_subscribed_cancelled", rpc_request["id"])
            raise
        finally:
            self._subscriptions.pop(rpc_request["id"], None)  # drop registry entry

    def authenticate(self, credentials: AuthenticationInfo) -> bool:
        return True  # No auth by default

    async def register_push_endpoint(
        self, config: TaskPushNotificationConfig
    ) -> TaskPushNotificationConfig:
        raise PushNotificationNotSupportedException()

    async def get_push_notification_config(
        self, params: TaskIdParams
    ) -> TaskPushNotificationConfig:
        raise PushNotificationNotSupportedException()

    async def subscribe_to_task_updates(
        self, params: TaskSendParams
    ) -> AsyncIterator[TaskStatusUpdateEvent | TaskArtifactUpdateEvent]:
        """
        Default fallback: poll get_task_status every 500 ms until terminal.
        """

        # inner async-generator does the actual yielding
        async def _stream() -> AsyncIterator[
            TaskStatusUpdateEvent | TaskArtifactUpdateEvent
        ]:
            last_state = None
            while True:
                task = await self.get_task_status(TaskQueryParams(id=params.id))
                # only yield on state-change
                if task.status.state != last_state:
                    yield TaskStatusUpdateEvent(**task.model_dump())
                    last_state = task.status.state

                if task.status.state in TERMINAL_TASK_STATES:
                    break

                await asyncio.sleep(0.5)

        return _stream()

    async def unsubscribe_task(self, params: TaskIdParams) -> Any:
        raise UnsupportedOperationException(
            f"Agent {self} does not support operation 'unsubscribe_task'"
        )

    async def cancel_task(self, params: TaskIdParams) -> Task:
        raise TaskNotCancelableException()

    async def get_agent_card(self) -> AgentCard:
        raise UnsupportedOperationException(
            f"Agent {self} does not support operation 'get_agent_card'"
        )

    async def get_task_status(self, params: TaskQueryParams) -> Task:
        raise UnsupportedOperationException(
            f"Agent {self} does not support operation 'get_task_status'"
        )

    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> Any:
        raise UnsupportedOperationException(
            f"Agent {self} does not support operation 'run_task'"
        )

    # ------------------------------------------------------------------ #
    #  (3)  Canonical signature required by Agent
    # ------------------------------------------------------------------ #
    async def start_task(self, params: TaskSendParams) -> Task:  # type: ignore[override]
        cls = self.__class__

        # --- Path A: subclass provided its own start_task ----------------
        if BaseAgent.start_task is not cls.start_task:
            return await cls.start_task(self, params)  # type: ignore[misc]

        # --- Path C: fallback to run_task -----------------------------
        if BaseAgent.run_task is not cls.run_task:
            parts = params.message.parts
            payload = None
            if parts:
                first = parts[0]
                if isinstance(first, TextPart):
                    payload = first.text
                elif isinstance(first, DataPart):
                    payload = first.data

            response_payload = await self.run_task(
                payload=payload,
                id=params.id,
            )

            return make_task(
                id=params.id,
                state=TaskState.COMPLETED,
                payload=response_payload,
            )

        # --- None of the above implemented ------------------------------
        raise NotImplementedError(
            f"{cls.__name__} must implement at least one of: "
            "`start_task()`, `start_task_simple()`, or `run_task()`."
        )

    def aserve(
        self,
        address: FameAddress | str,
        *,
        log_level: str | int | None = None,
        **kwargs,
    ):
        if not self._name:
            self._name = generate_id(mode="fingerprint", material=address)
        return super().aserve(address, log_level=log_level, **kwargs)
