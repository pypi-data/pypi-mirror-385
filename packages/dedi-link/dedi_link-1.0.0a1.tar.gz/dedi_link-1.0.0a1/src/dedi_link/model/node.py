"""
Node Model
"""

from uuid import uuid4
from typing import Optional
from pydantic import Field, ConfigDict, UUID4

from .base import JsonModel
from .crypto_key import Ec384PublicKey


class Node(JsonModel):
    """
    A node in a network

    A Node object represents a node in the network, a basic
    unit of operation and communication.
    """
    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=True,
    )

    node_id: UUID4 = Field(
        default_factory=uuid4,
        alias='nodeId',
        description='The unique ID of the node',
        examples=['a2342b55-c062-48f2-b047-c0ff3797dbc2']
    )
    node_name: str = Field(
        ...,
        alias='nodeName',
        description='The name of the node',
        examples=['Node A']
    )
    url: str = Field(
        ...,
        description='The URL of the node. pointing to the protocol discovery endpoint',
        examples=['https://node-a.example.com/api/.well-known/discovery-gateway']
    )
    description: str = Field(
        ...,
        description='A description of the node',
        examples=['This is Node A in the network.']
    )
    public_key: Optional[Ec384PublicKey] = Field(
        default=None,
        alias='publicKey',
        description='The ECDSA public key of the node using NIST P-384 curve, used to sign '
                    'and verify messages for secure communication',
        examples=[
            '-----BEGIN PUBLIC KEY-----\n'
            'MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEqGmo35lD1YBHifk2NFG9nz6KdTSBCOOH\n'
            '5ishmcprMRsKrHUXVokkmc2xETsegg5piN4hw5htSNLBz2zRDS1NbXPBxSAY4mTo\n'
            'TQeg8P94C0qKiaTV2XnHfUxSk/hn7E4B\n'
            '-----END PUBLIC KEY-----'
        ]
    )
    approved: bool = Field(
        default=False,
        description='Whether the node is approved for message exchange',
        examples=[True]
    )
