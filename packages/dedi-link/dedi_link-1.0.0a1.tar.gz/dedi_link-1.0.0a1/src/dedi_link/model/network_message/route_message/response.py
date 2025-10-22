"""
RouteResponse Message

This module defines the `RouteResponse` message, which is used to announce a
viable route to a specific node in the network.
"""

from typing import Literal
from pydantic import Field, ConfigDict, UUID4

from dedi_link.etc.enums import MessageType
from ..network_message import NetworkMessage


class RouteResponse(NetworkMessage):
    """
    A message to announce a viable route to a specific node in the network.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.ROUTE_RESPONSE] = Field(
        MessageType.ROUTE_RESPONSE,
        description='The type of the network message',
        alias='messageType',
    )
    target_node: UUID4 = Field(
        ...,
        description='The ID of the target node to route to',
        alias='targetNode',
    )
    route: list[UUID4] = Field(
        ...,
        description='The list of node IDs representing the route',
    )
