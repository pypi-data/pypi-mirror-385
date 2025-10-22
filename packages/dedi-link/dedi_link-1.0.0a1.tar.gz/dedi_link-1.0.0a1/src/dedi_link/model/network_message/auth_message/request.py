"""
A message to request joining a network.
"""

from typing import Literal
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from dedi_link.model.node import Node
from ..network_message import NetworkMessage


class AuthRequest(NetworkMessage):
    """
    A message to request joining a network.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.AUTH_REQUEST] = Field(
        MessageType.AUTH_REQUEST,
        description='The type of the network message',
        alias='messageType'
    )
    node: Node = Field(
        ...,
        description='The node representing the requester',
    )
    challenge_nonce: str = Field(
        ...,
        description='The nonce for the security challenge',
        alias='challengeNonce'
    )
    challenge_solution: int = Field(
        ...,
        description='The security challenge solution',
        alias='challengeSolution'
    )
    justification: str = Field(
        default='',
        description='The reason for the request',
    )
