"""
A message responding to a join request.
"""

from typing import Literal, Optional
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from dedi_link.model.network import Network
from ..management_key import NetworkManagementKey
from .invite_response import AuthInviteResponse


class AuthRequestResponse(AuthInviteResponse):
    """
    A message responding to a join request.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.AUTH_REQUEST_RESPONSE] = Field(
        MessageType.AUTH_REQUEST_RESPONSE,
        description='The type of the network message',
        alias='messageType'
    )
    network: Optional[Network] = Field(
        None,
        description='The network the requester is being invited to join, if accepted',
    )
    management_key: Optional[NetworkManagementKey] = Field(
        None,
        description='The management key for the network. If the network is decentralised, '
                    'this will be both the public and private keys; otherwise it will '
                    'just be the public key.',
        alias='managementKey'
    )
