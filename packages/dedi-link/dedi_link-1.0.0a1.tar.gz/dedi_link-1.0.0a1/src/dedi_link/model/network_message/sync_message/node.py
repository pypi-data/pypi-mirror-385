"""
A message to synchronise the known nodes across other nodes in the network.
"""

from typing import Literal
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from dedi_link.model.node import Node
from ..network_message import NetworkMessage


class SyncNode(NetworkMessage):
    """
    A message to synchronise the known nodes across other nodes in the network.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.SYNC_NODES] = Field(
        default=MessageType.SYNC_NODES,
        description='The type of the network message, indicating it is a sync nodes message.',
        alias='messageType'
    )

    nodes: list[Node] = Field(
        ...,
        description='The known nodes to be synchronized, including the current node.'
    )
