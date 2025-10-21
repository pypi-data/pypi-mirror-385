import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

from openhands.agent_server.models import (
    ConfirmationResponseRequest,
    EventPage,
    EventSortOrder,
    StoredConversation,
)
from openhands.agent_server.pub_sub import PubSub, Subscriber
from openhands.agent_server.utils import utc_now
from openhands.sdk import LLM, Agent, Event, Message, get_logger
from openhands.sdk.conversation.impl.local_conversation import LocalConversation
from openhands.sdk.conversation.secrets_manager import SecretValue
from openhands.sdk.conversation.state import AgentExecutionStatus, ConversationState
from openhands.sdk.event.conversation_state import ConversationStateUpdateEvent
from openhands.sdk.security.confirmation_policy import ConfirmationPolicyBase
from openhands.sdk.utils.async_utils import AsyncCallbackWrapper
from openhands.sdk.workspace import LocalWorkspace


logger = get_logger(__name__)


@dataclass
class EventService:
    """
    Event service for a conversation running locally, analogous to a conversation
    in the SDK. Async mostly for forward compatibility
    """

    stored: StoredConversation
    conversations_dir: Path
    working_dir: Path
    _conversation: LocalConversation | None = field(default=None, init=False)
    _pub_sub: PubSub[Event] = field(default_factory=lambda: PubSub[Event](), init=False)
    _run_task: asyncio.Task | None = field(default=None, init=False)

    @property
    def conversation_dir(self):
        return self.conversations_dir / self.stored.id.hex

    async def load_meta(self):
        meta_file = self.conversation_dir / "meta.json"
        self.stored = StoredConversation.model_validate_json(meta_file.read_text())

    async def save_meta(self):
        self.stored.updated_at = utc_now()
        meta_file = self.conversation_dir / "meta.json"
        meta_file.write_text(self.stored.model_dump_json())

    async def get_event(self, event_id: str) -> Event | None:
        if not self._conversation:
            raise ValueError("inactive_service")
        with self._conversation._state as state:
            index = state.events.get_index(event_id)
            event = state.events[index]
            return event

    async def search_events(
        self,
        page_id: str | None = None,
        limit: int = 100,
        kind: str | None = None,
        sort_order: EventSortOrder = EventSortOrder.TIMESTAMP,
    ) -> EventPage:
        if not self._conversation:
            raise ValueError("inactive_service")

        # Collect all events
        all_events = []
        with self._conversation._state as state:
            for event in state.events:
                # Apply kind filter if provided
                if (
                    kind is not None
                    and f"{event.__class__.__module__}.{event.__class__.__name__}"
                    != kind
                ):
                    continue
                all_events.append(event)

        # Sort events based on sort_order
        if sort_order == EventSortOrder.TIMESTAMP:
            all_events.sort(key=lambda x: x.timestamp)
        elif sort_order == EventSortOrder.TIMESTAMP_DESC:
            all_events.sort(key=lambda x: x.timestamp, reverse=True)

        # Handle pagination
        items = []
        start_index = 0

        # Find the starting point if page_id is provided
        if page_id:
            for i, event in enumerate(all_events):
                if event.id == page_id:
                    start_index = i
                    break

        # Collect items for this page
        next_page_id = None
        for i in range(start_index, len(all_events)):
            if len(items) >= limit:
                # We have more items, set next_page_id
                if i < len(all_events):
                    next_page_id = all_events[i].id
                break
            items.append(all_events[i])

        return EventPage(items=items, next_page_id=next_page_id)

    async def count_events(
        self,
        kind: str | None = None,
    ) -> int:
        """Count events matching the given filters."""
        if not self._conversation:
            raise ValueError("inactive_service")

        count = 0
        with self._conversation._state as state:
            for event in state.events:
                # Apply kind filter if provided
                if (
                    kind is not None
                    and f"{event.__class__.__module__}.{event.__class__.__name__}"
                    != kind
                ):
                    continue
                count += 1

        return count

    async def batch_get_events(self, event_ids: list[str]) -> list[Event | None]:
        """Given a list of ids, get events (Or none for any which were not found)"""
        results = []
        for event_id in event_ids:
            result = await self.get_event(event_id)
            results.append(result)
        return results

    async def send_message(self, message: Message, run: bool = False):
        if not self._conversation:
            raise ValueError("inactive_service")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._conversation.send_message, message)
        if run:
            with self._conversation.state as state:
                run = state.agent_status != AgentExecutionStatus.RUNNING
        if run:
            loop.run_in_executor(None, self._conversation.run)

    async def subscribe_to_events(self, subscriber: Subscriber[Event]) -> UUID:
        subscriber_id = self._pub_sub.subscribe(subscriber)

        # Send current state to the new subscriber immediately
        if self._conversation:
            state = self._conversation._state
            with state:
                # Create state update event with current state information
                state_update_event = (
                    ConversationStateUpdateEvent.from_conversation_state(state)
                )

                # Send state update directly to the new subscriber
                try:
                    await subscriber(state_update_event)
                except Exception as e:
                    logger.error(
                        f"Error sending initial state to subscriber "
                        f"{subscriber_id}: {e}"
                    )

        return subscriber_id

    async def unsubscribe_from_events(self, subscriber_id: UUID) -> bool:
        return self._pub_sub.unsubscribe(subscriber_id)

    async def start(self):
        # Store the main event loop for cross-thread communication
        self._main_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        # self.stored contains an Agent configuration we can instantiate
        self.conversation_dir.mkdir(parents=True, exist_ok=True)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        agent = Agent.model_validate(self.stored.agent.model_dump())
        # Convert workspace to LocalWorkspace if needed
        workspace = self.stored.workspace
        if not isinstance(workspace, LocalWorkspace):
            workspace = LocalWorkspace(working_dir=workspace.working_dir)
        conversation = LocalConversation(
            agent=agent,
            workspace=workspace,
            persistence_dir=str(self.conversations_dir),
            conversation_id=self.stored.id,
            callbacks=[
                AsyncCallbackWrapper(self._pub_sub, loop=asyncio.get_running_loop())
            ],
            max_iteration_per_run=self.stored.max_iterations,
            stuck_detection=self.stored.stuck_detection,
            visualize=False,
            secrets=self.stored.secrets,
        )

        # Set confirmation mode if enabled
        conversation.set_confirmation_policy(self.stored.confirmation_policy)
        self._conversation = conversation

        # Register state change callback to automatically publish updates
        self._conversation._state.set_on_state_change(self._conversation._on_event)

        # Publish initial state update
        await self._publish_state_update()

    async def run(self):
        """Run the conversation asynchronously."""
        if not self._conversation:
            raise ValueError("inactive_service")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._conversation.run)

    async def respond_to_confirmation(self, request: ConfirmationResponseRequest):
        if request.accept:
            await self.run()
        else:
            await self.pause()

    async def pause(self):
        if self._conversation:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._conversation.pause)

    async def update_secrets(self, secrets: dict[str, SecretValue]):
        """Update secrets in the conversation."""
        if not self._conversation:
            raise ValueError("inactive_service")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._conversation.update_secrets, secrets)

    async def set_confirmation_policy(self, policy: ConfirmationPolicyBase):
        """Set the confirmation policy for the conversation."""
        if not self._conversation:
            raise ValueError("inactive_service")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self._conversation.set_confirmation_policy, policy
        )

    async def close(self):
        await self._pub_sub.close()
        if self._conversation:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, self._conversation.close)

    async def generate_title(
        self, llm: "LLM | None" = None, max_length: int = 50
    ) -> str:
        """Generate a title for the conversation.

        Resolves the provided LLM via the conversation's registry if a usage_id is
        present, registering it if needed. Then delegates to LocalConversation in an
        executor to avoid blocking the event loop.
        """
        if not self._conversation:
            raise ValueError("inactive_service")

        resolved_llm = llm
        if llm is not None:
            usage_id = llm.usage_id
            try:
                resolved_llm = self._conversation.llm_registry.get(usage_id)
            except KeyError:
                self._conversation.llm_registry.add(llm)
                resolved_llm = llm

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._conversation.generate_title, resolved_llm, max_length
        )

    async def get_state(self) -> ConversationState:
        if not self._conversation:
            raise ValueError("inactive_service")
        return self._conversation._state

    async def _publish_state_update(self):
        """Publish a ConversationStateUpdateEvent with the current state."""
        if not self._conversation:
            return

        state = self._conversation._state
        with state:
            # Create state update event with current state information
            state_update_event = ConversationStateUpdateEvent.from_conversation_state(
                state
            )

            # Publish the state update event
            await self._pub_sub(state_update_event)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.save_meta()
        await self.close()
