"""
A message to request another node to synchronise its data.
"""

from typing import Literal
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType, SyncRequestType
from ..network_message import NetworkMessage


class SyncRequest(NetworkMessage):
    """
    A message to request another node to synchronise its data.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.SYNC_REQUEST] = Field(
        default=MessageType.SYNC_REQUEST,
        description='The type of the network message, indicating it is a sync request message.',
        alias='messageType'
    )
    target: SyncRequestType = Field(
        ...,
        description='The type of data being requested from the node.'
    )
