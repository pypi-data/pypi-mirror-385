"""
A module defining the User model.
"""


from uuid import uuid4
from pydantic import Field, ConfigDict, UUID4

from .base import JsonModel


class User(JsonModel):
    """
    A class representing a user in the system.
    """

    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=True,
    )

    user_id: UUID4 = Field(
        default_factory=uuid4,
        alias='userId',
        description='Unique user ID in UUID4 format',
        examples=['5a639534-d547-4242-b53d-43e7bd77b138']
    )
