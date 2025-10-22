"""
A model to hold network management keys.
"""

from typing import Optional
from pydantic import Field, ConfigDict

from ..base import JsonModel
from ..crypto_key import Ec384PublicKey, Ec384PrivateKey


class NetworkManagementKey(JsonModel):
    """
    A model to hold network management keys.
    """
    model_config = ConfigDict(
        extra='forbid',
        serialize_by_alias=True,
    )

    public_key: Ec384PublicKey = Field(
        ...,
        description='The ECDSA P384 public key for the network management',
        alias='publicKey',
        examples=[
            '-----BEGIN PUBLIC KEY-----\n'
            'MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE8szFU6rSdHUEwTKp1YYdbbsoQ/fNnBhR\n'
            'kmKoa6hQd5tZds1f/LlRXdtSOfp6vW3BhVxVUv0AgqzhfMljnjfWrFBLctvZu+Kc\n'
            'jfvizlz2kfcPGukK2jxYbrZNj4PbT6XB\n'
            '-----END PUBLIC KEY-----'
        ]
    )
    private_key: Optional[Ec384PrivateKey] = Field(
        None,
        description='The ECDSA P384 private key for the network management. Only sent to another '
                    'node when the network is managed in a decentralised manner.',
        alias='privateKey',
        examples=[
            '-----BEGIN PRIVATE KEY-----\n'
            'MIG2AgEAMBAGByqGSM49AgEGBSuBBAAiBIGeMIGbAgEBBDDBenD1/QEMZGpLScB0\n'
            'fk8xSeTw1QI8x5WkdGhqvMOJ0acxK4h6BEXN+DR6lNHDYByhZANiAATyzMVTqtJ0\n'
            'dQTBMqnVhh1tuyhD982cGFGSYqhrqFB3m1l2zV/8uVFd21I5+nq9bcGFXFVS/QCC\n'
            'rOF8yWOeN9asUEty29m74pyN++LOXPaR9w8a6QraPFhutk2Pg9tPpcE=\n'
            '-----END PRIVATE KEY-----'
        ]
    )
