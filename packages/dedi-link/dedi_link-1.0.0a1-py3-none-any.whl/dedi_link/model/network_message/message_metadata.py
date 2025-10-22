"""
Metadata for a message in the Decentralised Discovery Gateway network protocol.
"""

import time
from uuid import uuid4
from pydantic import Field, ConfigDict, UUID4

from ..base import JsonModel


class MessageMetadata(JsonModel):
    """
    Metadata for a message in the Decentralised Discovery Gateway network protocol.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    network_id: UUID4 = Field(
        ...,
        description="The unique ID of the network",
        alias='networkId'
    )
    node_id: UUID4 = Field(
        ...,
        description="The unique ID of the node that sent the message",
        alias='nodeId'
    )
    message_id: UUID4 = Field(
        default_factory=uuid4,
        description="The unique ID of the message",
        alias='messageId'
    )
    timestamp: float = Field(
        default_factory=time.time,
        description="The timestamp when the message was sent, in seconds since the epoch",
        alias='timestamp'
    )
