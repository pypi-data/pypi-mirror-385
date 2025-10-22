"""
RouteEnvelope class for routing messages in the network.

This class is used to wrap another message for routing purposes in a federated network.
"""

from typing import Literal
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from ..network_message import NetworkMessage


class RouteEnvelope(NetworkMessage):
    """
    A message to envelope another message for proxy routing.

    For model validation, this class should be extended with your custom message
    classes to handle routing business logic messages.
    """

    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.ROUTE_ENVELOPE] = Field(
        MessageType.ROUTE_ENVELOPE,
        description='The type of the network message',
        alias='messageType',
    )
    enveloped_headers: dict = Field(
        default_factory=dict,
        description='The headers of the enveloped message. Only business logic relevant '
                    'headers should be included. Things like "Accept-Encoding" should be omitted.',
        alias='envelopedHeaders',
    )
    enveloped_message: dict = Field(
        ...,
        description='The actual enveloped message as a dictionary. It\'s recommended to '
                    'override this field to be a discriminated union including your business '
                    'logic message types for proper validation.',
        alias='envelopedMessage',
    )
