"""
Proof of Work module for Decentralised Discovery Gateway (DDG) service.

All implementation of the Decentralised Discovery Link protocol needs a similar module
to handle Proof of Work (PoW) operations. This library provides one (probably not the
most efficient) implementation of PoW. It uses OpenSSL in C on Windows and Linux whenever
possible, and falls back to a pure Python implementation if the CFFI module cannot be used.
"""

from .libpow import PowDriver
