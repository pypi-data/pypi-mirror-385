"""
A message to notify the network about an event, whether it be
a node joining, leaving, or any other significant event related
to authorisation and authentication.
"""

from typing import Literal
from pydantic import Field, ConfigDict, UUID4

from dedi_link.etc.enums import MessageType, AuthNotificationType
from ..network_message import NetworkMessage


class AuthNotification(NetworkMessage):
    """
    A message to notify the network about an event, whether it be
    a node joining, leaving, or any other significant event related
    to authorisation and authentication.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.AUTH_NOTIFICATION] = Field(
        MessageType.AUTH_NOTIFICATION,
        description='The type of the network message',
        alias='messageType'
    )
    reason: AuthNotificationType = Field(
        ...,
        description='The reason for the notification',
    )
    affected_node_id: UUID4 = Field(
        ...,
        description='The ID of the node that triggered the notification',
        alias='affectedNodeId'
    )
