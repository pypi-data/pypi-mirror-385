"""
Network Message Model
"""

from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from ..base import JsonModel
from .message_metadata import MessageMetadata


class NetworkMessage(JsonModel):
    """
    Base class for a Network Message
    """
    model_config = ConfigDict(
        serialize_by_alias=True,
    )

    metadata: MessageMetadata = Field(
        ...,
        description="Metadata for the network message",
    )
    message_type: MessageType = Field(
        ...,
        description="The type of the network message",
        alias='messageType'
    )
