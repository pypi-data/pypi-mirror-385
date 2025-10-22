"""
Module defining the Network model for representing a network of nodes sharing data.
"""

from uuid import uuid4
from pydantic import Field, ConfigDict, UUID4

from .base import JsonModel


class Network(JsonModel):
    """
    A network that contains nodes which agreed to share data among each other.

    A network is a logical abstraction of a group of nodes that accepts (partially)
    others' credentials and allows access to their data.
    """

    model_config = ConfigDict(
        serialize_by_alias=True,
    )

    network_id: UUID4 = Field(
        default_factory=uuid4,
        alias='networkId',
        description='The unique ID of the network',
        examples=['29c16129-8333-484e-b8de-d53ffa14092d']
    )
    network_name: str = Field(
        ...,
        alias='networkName',
        description='The name of the network',
        examples=['Cancer Research Network']
    )
    description: str = Field(
        default='',
        description='A description of the network',
        examples=['A network for sharing cancer research data among participating nodes.']
    )
    node_ids: list[UUID4] = Field(
        default_factory=list,
        alias='nodeIds',
        description='The IDs of the nodes in the network',
        examples=[
            ['a2342b55-c062-48f2-b047-c0ff3797dbc2'],
        ]
    )
    visible: bool = Field(
        default=False,
        description='Whether the network is visible to others to apply for joining',
        examples=[True]
    )
    registered: bool = Field(
        default=False,
        description='Whether the network is registered in a public registry',
        examples=[True]
    )
    instance_id: UUID4 = Field(
        default_factory=uuid4,
        alias='instanceId',
        description='The unique ID of the network instance',
        examples=['5baad7ec-54ff-4b5f-9bd1-e3b8ada8f3f7']
    )
    central_node: UUID4 | None = Field(
        default=None,
        alias='centralNode',
        description='The ID of the central node for permission and identity management. '
                    'None if the permission is decentralised.',
        examples=['5baad7ec-54ff-4b5f-9bd1-e3b8ada8f3f7']
    )
