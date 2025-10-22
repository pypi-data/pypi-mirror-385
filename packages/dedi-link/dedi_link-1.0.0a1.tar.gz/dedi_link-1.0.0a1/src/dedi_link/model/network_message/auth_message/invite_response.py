"""
A response message to an invitation to join a network.
"""

from typing import Literal, Optional
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from dedi_link.model.node import Node
from ..network_message import NetworkMessage


class AuthInviteResponse(NetworkMessage):
    """
    A message responding to an invitation to join a network.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.AUTH_INVITE_RESPONSE] = Field(
        MessageType.AUTH_INVITE_RESPONSE,
        description='The type of the network message',
        alias='messageType'
    )
    approved: bool = Field(
        ...,
        description='Whether the invitation is accepted or not',
    )
    node: Optional[Node] = Field(
        None,
        description='The node representing the responder, if accepted',
    )
    justification: str = Field(
        default='',
        description='The reason for the response',
    )
