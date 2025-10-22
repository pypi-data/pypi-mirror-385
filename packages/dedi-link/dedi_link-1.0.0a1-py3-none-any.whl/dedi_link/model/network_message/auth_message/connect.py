"""
A message used to authenticate with another node and initiate a connection.
"""

from typing import Literal
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from ..network_message import NetworkMessage


class AuthConnect(NetworkMessage):
    """
    A message responding to an invitation to join a network.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.AUTH_CONNECT] = Field(
        MessageType.AUTH_CONNECT,
        description='The type of the network message',
        alias='messageType'
    )
