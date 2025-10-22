"""
RouteNotification Message

This module defines the `RouteNotification` message, which is used to notify
the network that a node either went offline or broke the existing route.
"""

from typing import Literal
from pydantic import Field, ConfigDict, UUID4

from dedi_link.etc.enums import MessageType
from ..network_message import NetworkMessage


class RouteNotification(NetworkMessage):
    """
    A message to notify the network that a node either went offline,
    or broke the existing route.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.ROUTE_NOTIFICATION] = Field(
        MessageType.ROUTE_NOTIFICATION,
        description='The type of the network message',
        alias='messageType',
    )
    target_node: UUID4 = Field(
        ...,
        description='The ID of the target node to route to',
        alias='targetNode',
    )
