"""
A message to invite a node to an existing network.
"""

from typing import Literal
from pydantic import Field, ConfigDict

from dedi_link.etc.enums import MessageType
from dedi_link.model.network import Network
from dedi_link.model.node import Node
from ..management_key import NetworkManagementKey
from .request import AuthRequest


class AuthInvite(AuthRequest):
    """
    A message to invite a node to an existing network.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    message_type: Literal[MessageType.AUTH_INVITE] = Field(
        MessageType.AUTH_INVITE,
        description='The type of the network message',
        alias='messageType'
    )
    network: Network = Field(
        ...,
        description='The network to which the node is being invited.'
    )
    node: Node = Field(
        ...,
        description='The node inviting the new node to the network.',
    )
    management_key: NetworkManagementKey = Field(
        ...,
        description='The management key for the network. If the network is decentralised, '
                    'this will be both the public and private keys; otherwise it will '
                    'just be the public key.',
        alias='managementKey'
    )
