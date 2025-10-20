"""
Generated Python class from team-message-event.schema.yaml
This file is auto-generated. Do not edit manually.
"""

from .message import Message
from .event import Event

class TeamMessageEvent(Event):
    """Event occurring when a message has been received from a teammate"""

    def __init__(self, message: str | None, message_type: str | None, sender_id: int | None, turn_number: int | None, type: 'Message.Type | None'):
        if type is None:
            raise ValueError("The 'type' parameter must be provided.")
        if turn_number is None:
            raise ValueError("The 'turn_number' parameter must be provided.")
        if message is None:
            raise ValueError("The 'message' parameter must be provided.")
        if message_type is None:
            raise ValueError("The 'message_type' parameter must be provided.")
        if sender_id is None:
            raise ValueError("The 'sender_id' parameter must be provided.")
        super().__init__(turn_number, type)
        self.message = message
        self.message_type = message_type
        self.sender_id = sender_id
