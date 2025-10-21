"""Message Handler Mixin for ALL agents to communicate via orchestrator's message queue.

CRITICAL ARCHITECTURAL PRINCIPLE:
ALL inter-agent communication MUST go through the orchestrator. Agents NEVER send
messages directly to each other. This enables:

1. Central routing & load balancing (orchestrator can use alternate agents)
2. Bottleneck detection (all task durations measured in one place)
3. Velocity metrics (orchestrator tracks all agent performance)
4. Flexibility (agents suggest recipients, orchestrator decides)

Architecture:
    ┌─────────────────────────────────────────────────────┐
    │              ORCHESTRATOR (Message Broker)          │
    │  • Receives ALL messages from ALL agents            │
    │  • Routes to best available agent                   │
    │  • Measures task duration for ALL tasks             │
    │  • Detects bottlenecks and optimizes routing        │
    └─────────────────────────────────────────────────────┘
         ↑                    ↓                    ↑
         │                    │                    │
         │     ┌──────────────┼──────────────┐     │
         │     ↓              ↓              ↓     │
    user_listener    project_manager    code_developer
         ↑                ↑                 ↑
         └────────────────┴─────────────────┘
              ALL send to orchestrator
              (never directly to each other)

Example Flow:
    User: "Implement feature X"
    ↓
    user_listener → orchestrator (USER_REQUEST, suggested_recipient: "project_manager")
    ↓
    orchestrator: routes to project_manager (measures start time)
    ↓
    project_manager → orchestrator (TASK_REQUEST, suggested_recipient: "architect", reason: "Need spec")
    ↓
    orchestrator: routes to architect (measures project_manager duration)
    ↓
    architect → orchestrator (TASK_REQUEST, suggested_recipient: "code_developer", reason: "Spec ready")
    ↓
    orchestrator: routes to code_developer (measures architect duration)
    ↓
    code_developer → orchestrator (USER_RESPONSE, recipient: "user_listener")
    ↓
    orchestrator: routes to user_listener (measures code_developer duration)
    ↓
    user_listener displays: "✅ Feature X implemented! PR #123"

Metrics Collected:
- project_manager: 5 min (ROADMAP entry creation)
- architect: 120 min (spec creation)
- code_developer: 180 min (implementation)
- Total: 305 min (5h 5min)
"""

import logging
import time
from typing import Optional, Callable

from coffee_maker.autonomous.message_queue import (
    MessageQueue,
    Message,
    MessageType,
    AgentType,
)

logger = logging.getLogger(__name__)


class MessageHandlerMixin:
    """Mixin for user_listener to handle message queue communication.

    This mixin adds message queue capabilities to user_listener, enabling it to:
    - Send user requests to assistant for classification
    - Receive delegation responses from assistant
    - Forward tasks to appropriate agents
    - Receive and display responses from agents
    - Poll for messages in the background
    """

    def __init__(self, *args, **kwargs):
        """Initialize message queue connection.

        Note: This is a mixin, so it calls super().__init__() to support
        cooperative multiple inheritance.
        """
        super().__init__(*args, **kwargs)
        self.message_queue = MessageQueue()
        self.agent_id = AgentType.USER_LISTENER.value
        self._message_handlers = {
            MessageType.USER_RESPONSE.value: self._handle_user_response,
            MessageType.STATUS_UPDATE.value: self._handle_status_update,
        }
        logger.info(f"{self.agent_id} connected to message queue")

    def send_user_request(
        self, user_input: str, suggested_recipient: Optional[str] = None, callback: Optional[Callable] = None
    ) -> None:
        """Send user request to orchestrator for routing.

        The orchestrator will analyze the request and route it to the appropriate agent.
        You can suggest a recipient, but orchestrator may choose a different agent based
        on availability and load balancing.

        Args:
            user_input: The user's input text
            suggested_recipient: Optional suggestion for which agent should handle this
            callback: Optional callback to invoke when response received
        """
        message = Message(
            sender=self.agent_id,
            recipient="orchestrator",  # ALL messages go to orchestrator
            type=MessageType.USER_REQUEST.value,
            payload={
                "user_input": user_input,
                "suggested_recipient": suggested_recipient,  # Orchestrator may override
                "callback_id": id(callback) if callback else None,
            },
            priority=1,  # High priority for user requests
        )

        self.message_queue.send(message)
        logger.info(f"Sent USER_REQUEST to orchestrator: {user_input[:50]}...")

        # Display to user that request is being processed
        print(f"\n🔄 Processing request: {user_input}")
        if suggested_recipient:
            print(f"   Suggesting: {suggested_recipient}")
        print("   Orchestrator is routing to appropriate agent...\n")

        # Store callback for later invocation
        if callback:
            if not hasattr(self, "_callbacks"):
                self._callbacks = {}
            self._callbacks[id(callback)] = callback

    def send_task_request(
        self,
        task: str,
        suggested_recipient: str,
        reason: str = "",
        priority: int = 5,
        callback: Optional[Callable] = None,
    ) -> None:
        """Send task request to another agent (through orchestrator).

        IMPORTANT: This sends to orchestrator, NOT directly to the suggested agent.
        Orchestrator may route to a different agent if suggested one is busy/unavailable.

        Args:
            task: Description of the task to perform
            suggested_recipient: Agent you think should handle this (orchestrator may override)
            reason: Why this agent should handle it (helps orchestrator decide)
            priority: Task priority (1=highest, 10=lowest)
            callback: Optional callback when task completes
        """
        message = Message(
            sender=self.agent_id,
            recipient="orchestrator",  # ALL inter-agent messages go to orchestrator
            type=MessageType.TASK_REQUEST.value,
            payload={
                "task": task,
                "suggested_recipient": suggested_recipient,
                "reason": reason,
                "callback_id": id(callback) if callback else None,
            },
            priority=priority,
        )

        self.message_queue.send(message)
        logger.info(
            f"{self.agent_id} sent TASK_REQUEST to orchestrator (suggesting {suggested_recipient}): {task[:50]}..."
        )

        # Store callback
        if callback:
            if not hasattr(self, "_callbacks"):
                self._callbacks = {}
            self._callbacks[id(callback)] = callback

    def send_response(self, response: str, recipient: str, original_task_id: Optional[str] = None) -> None:
        """Send response back to requesting agent (through orchestrator).

        Args:
            response: Response text/data
            recipient: Agent to send response to
            original_task_id: ID of the original task (for tracking)
        """
        # Responses can go directly to recipient OR through orchestrator
        # For user_listener, we send directly. For other agents, through orchestrator.
        if recipient == AgentType.USER_LISTENER.value:
            # Send directly to user_listener (orchestrator doesn't need to route UI responses)
            target = recipient
        else:
            # Send through orchestrator for metrics/tracking
            target = "orchestrator"

        message = Message(
            sender=self.agent_id,
            recipient=target,
            type=(
                MessageType.USER_RESPONSE.value
                if recipient == AgentType.USER_LISTENER.value
                else MessageType.TASK_RESPONSE.value
            ),
            payload={"response": response, "original_task_id": original_task_id, "final_recipient": recipient},
            priority=2,  # Medium-high priority for responses
        )

        self.message_queue.send(message)
        logger.info(f"{self.agent_id} sent response to {recipient}: {response[:50]}...")

    def poll_messages(self, timeout: float = 0.1) -> None:
        """Poll for incoming messages and handle them.

        Args:
            timeout: How long to wait for messages (seconds)
        """
        message = self.message_queue.get(recipient=self.agent_id, timeout=timeout)

        if message:
            logger.debug(f"Received message: {message.type} from {message.sender}")

            # Mark as started
            self.message_queue.mark_started(message.task_id, agent=self.agent_id)

            # Handle based on type
            handler = self._message_handlers.get(message.type)
            if handler:
                try:
                    handler(message)
                    self.message_queue.mark_completed(
                        message.task_id,
                        duration_ms=int(
                            (time.time() - time.mktime(time.strptime(message.timestamp, "%Y-%m-%dT%H:%M:%S.%f"))) * 1000
                        ),
                    )
                except Exception as e:
                    logger.error(f"Error handling message {message.type}: {e}")
                    self.message_queue.mark_failed(message.task_id, error_message=str(e))
            else:
                logger.warning(f"No handler for message type: {message.type}")
                self.message_queue.mark_completed(message.task_id, duration_ms=0)

    def _handle_user_response(self, message: Message) -> None:
        """Handle response from an agent to display to user.

        Args:
            message: Message containing response payload
        """
        response_text = message.payload.get("response", "")
        agent_name = message.sender

        # Display response to user in console
        print(f"\n{'='*60}")
        print(f"📨 Response from {agent_name}:")
        print(f"{'='*60}")
        print(response_text)
        print(f"{'='*60}\n")

        # Invoke callback if one was registered
        callback_id = message.payload.get("callback_id")
        if callback_id and hasattr(self, "_callbacks") and callback_id in self._callbacks:
            self._callbacks[callback_id](response_text)
            del self._callbacks[callback_id]

    def _handle_status_update(self, message: Message) -> None:
        """Handle status update from any agent.

        Args:
            message: Message containing status info
        """
        status = message.payload.get("status", "")
        agent_name = message.sender

        # Display status update
        print(f"\n🔄 Status update from {agent_name}: {status}")
