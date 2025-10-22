"""
RouteRequest Message

This module defines the `RouteRequest` message, which is used to request a
viable route to a specific node in the network.
"""

from typing import Literal
from pydantic import Field, ConfigDict, UUID4

from dedi_link.etc.enums import MessageType
from ..network_message import NetworkMessage


class RouteRequest(NetworkMessage):
    """
    A message to request a viable route to a specific node in the network.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.ROUTE_REQUEST] = Field(
        MessageType.ROUTE_REQUEST,
        description='The type of the network message',
        alias='messageType',
    )
    target_node: UUID4 = Field(
        ...,
        description='The ID of the target node to route to',
        alias='targetNode',
    )
