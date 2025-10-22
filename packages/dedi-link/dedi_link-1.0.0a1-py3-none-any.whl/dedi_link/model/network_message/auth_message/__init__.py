"""
This module defines messages related to network joining, invitations, and other
authentication-related interactions within the network.
"""

from typing import Annotated, Union
from pydantic import Field

from .invite import AuthInvite
from .invite_response import AuthInviteResponse
from .request import AuthRequest
from .request_response import AuthRequestResponse
from .connect import AuthConnect
from .notification import AuthNotification


AuthRequestUnion = Annotated[
    Union[AuthRequest, AuthInvite],
    Field(
        description='Union type for either a join request or an invite',
        discriminator='message_type',
    )
]


AuthResponseUnion = Annotated[
    Union[AuthRequestResponse, AuthInviteResponse],
    Field(
        description='Union type for either a response to a join request or an invite',
        discriminator='message_type',
    )
]
