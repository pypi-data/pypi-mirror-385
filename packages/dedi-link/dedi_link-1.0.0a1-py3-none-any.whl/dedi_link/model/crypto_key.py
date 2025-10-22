"""
Module for cryptographic key representation and validation.
"""

from abc import ABC, abstractmethod
from typing import Any
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from pydantic_core import core_schema


class CryptoKey(ABC):
    """
    Base class for cryptographic keys.
    """

    __slots__ = ()

    @abstractmethod
    def _identity_bytes(self) -> bytes:
        """
        Get the identity bytes of the key for comparison and hashing.
        :return: The identity bytes.
        """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CryptoKey):
            return NotImplemented

        return self._identity_bytes() == other._identity_bytes()

    def __hash__(self) -> int:
        return hash(self._identity_bytes())


class Ec384PublicKey(CryptoKey):
    """
    A type representing an ECDSA public key using the NIST P-384 curve,
    """

    __slots__ = ('public_key',)

    def __init__(self, public_key: ec.EllipticCurvePublicKey):
        self.public_key = public_key

    def _identity_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @classmethod
    def _try_parse(cls, value: Any) -> 'Ec384PublicKey':
        """
        Parse and validate that the provided value is a valid ECDSA public key
        using NIST P-384 curve.
        :param value: The public key in PEM format.
        :return: The ECDSA public key object.
        """
        if isinstance(value, Ec384PublicKey):
            return value

        if not isinstance(value, str):
            raise TypeError('Public key must be a string in PEM format.')

        try:
            public_key = serialization.load_pem_public_key(
                value.encode()
            )
        except Exception as e:
            raise ValueError('Invalid public key format.') from e

        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise ValueError('The provided key is not an ECDSA public key.')

        if not isinstance(public_key.curve, ec.SECP384R1):
            raise ValueError('The ECDSA public key must use the NIST P-384 curve.')

        return cls(public_key)

    @classmethod
    def _try_serialise(cls, value: Any):
        """
        Serialize the ECDSA public key to PEM format.
        :param value: The ECDSA public key object.
        :return: The public key in PEM format as a string.
        """
        if not isinstance(value, Ec384PublicKey):
            raise TypeError('Value must be an ECDSA public key.')

        pem = value.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __):
        return core_schema.no_info_after_validator_function(
            cls._try_parse,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._try_serialise,
                when_used='json-unless-none',
            )
        )


class Ec384PrivateKey(CryptoKey):
    """
    A type representing an ECDSA private key using the NIST P-384 curve,
    """

    __slots__ = ('private_key',)

    def __init__(self, private_key: ec.EllipticCurvePrivateKey):
        self.private_key = private_key

    def _identity_bytes(self) -> bytes:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

    @classmethod
    def _try_parse(cls, value: Any) -> 'Ec384PrivateKey':
        """
        Parse and validate that the provided value is a valid ECDSA private key
        using NIST P-384 curve.
        :param value: The private key in PEM format.
        :return: The ECDSA private key object.
        """
        if isinstance(value, Ec384PrivateKey):
            return value

        if not isinstance(value, str):
            raise TypeError('Private key must be a string in PEM format.')

        try:
            private_key = serialization.load_pem_private_key(
                value.encode(),
                password=None
            )
        except Exception as e:
            raise ValueError('Invalid private key format.') from e

        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            raise ValueError('The provided key is not an ECDSA private key.')

        if not isinstance(private_key.curve, ec.SECP384R1):
            raise ValueError('The ECDSA private key must use the NIST P-384 curve.')

        return cls(private_key)

    @classmethod
    def _try_serialise(cls, value: Any):
        """
        Serialize the ECDSA private key to PEM format.
        :param value: The ECDSA private key object.
        :return: The private key in PEM format as a string.
        """
        if not isinstance(value, Ec384PrivateKey):
            raise TypeError('Value must be an ECDSA private key.')

        pem = value.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode()

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __):
        return core_schema.no_info_after_validator_function(
            cls._try_parse,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._try_serialise,
                when_used='json-unless-none',
            )
        )
