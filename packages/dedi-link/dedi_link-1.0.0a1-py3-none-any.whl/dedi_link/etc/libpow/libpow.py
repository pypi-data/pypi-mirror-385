"""
Proof of Work Driver
"""

import sys
import os
import asyncio
import hashlib
import importlib.resources as pkg_resources
from concurrent.futures import ProcessPoolExecutor
from cffi import FFI


ffi = FFI()
ffi.cdef("""
    int solve_pow(const char *nonce, int difficulty, unsigned long long *result);
""")


class PowDriver:
    """
    A class to handle proof of work challenges using a native C library,
    falling back to Python implementation if the library is not available.
    """
    _lib = None
    _executor = ProcessPoolExecutor()

    @property
    def lib(self):
        """
        C library getter.
        :return: The Lib object from CFFI interface, pointing to the native library.
        """
        if self._lib is None:
            if sys.platform == 'win32':
                lib_name = 'libpow.dll'
            elif sys.platform == 'darwin':
                raise RuntimeError("Native library is not available on macOS")
            else:
                lib_name = 'libpow.so'

            try:
                lib_path = pkg_resources.files('dedi_link.data.bin') / lib_name
            except (ImportError, FileNotFoundError, AttributeError) as e:
                raise RuntimeError(f"Native library {lib_name} not found") from e

            if not os.path.exists(lib_path):
                raise RuntimeError(f"Native library {lib_path} not found")

            if sys.platform == 'win32':
                os.add_dll_directory(str(lib_path.parent))
            PowDriver._lib = ffi.dlopen(str(lib_path))

        return self._lib

    def _c_solve(self, nonce: str, difficulty: int) -> int:
        """
        Solve a proof of work challenge with CFFI interface.

        This function calls a custom C library for native acceleration of the
        SHA-256 hashing.
        :param nonce: The nonce to use for the proof of work challenge.
        :param difficulty: How many leading zeros the hash should have.
        :return: The valid nonce that solves the challenge.
        """
        if not isinstance(nonce, str) or not isinstance(difficulty, int):
            raise TypeError('Expected nonce: str and difficulty: int')

        res_ptr = ffi.new('unsigned long long *')
        ret = self.lib.solve_pow(nonce.encode(), difficulty, res_ptr)

        if ret != 0:
            raise RuntimeError('PoW solving failed')

        return res_ptr[0]

    @staticmethod
    def _python_solve(nonce: str, difficulty: int) -> int:
        """
        Solve a proof of work challenge with Python implementation.

        This is a fallback implementation that uses Python's hashlib
        to compute the SHA-256 hash and find a valid nonce.
        :param nonce: The nonce to use for the proof of work challenge.
        :param difficulty: How many leading zeros the hash should have.
        :return: The valid nonce that solves the challenge.
        """
        if not isinstance(nonce, str) or not isinstance(difficulty, int):
            raise TypeError('Expected nonce: str and difficulty: int')
        if difficulty < 1 or difficulty > 256:
            raise ValueError('Difficulty must be between 1 and 256')

        target_prefix = '0' * difficulty

        for counter in range(1 << 64):  # covers entire 64-bit unsigned range
            data = f'{nonce}{counter}'.encode()
            digest = hashlib.sha256(data).hexdigest()
            bin_hash = bin(int(digest, 16))[2:].zfill(256)

            if bin_hash.startswith(target_prefix):
                return counter

        raise RuntimeError('No valid nonce found within 64-bit search space')

    def solve(self, nonce: str, difficulty: int) -> int:
        """
        Solve a proof of work challenge.
        :param nonce: The nonce to use for the proof of work challenge.
        :param difficulty: How many leading zeros the hash should have.
        :return: The valid nonce that solves the challenge.
        """
        try:
            return self._c_solve(nonce, difficulty)
        except OSError:
            return self._python_solve(nonce, difficulty)

    async def solve_async(self, nonce: str, difficulty: int) -> int:
        """
        Asynchronous version of the solve method.

        This function uses a ProcessPoolExecutor to run the solve method
        in a separate process, allowing it to run without blocking the event loop.
        :param nonce: The nonce to use for the proof of work challenge.
        :param difficulty: How many leading zeros the hash should have.
        :return: The valid nonce that solves the challenge.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.solve,
            nonce,
            difficulty,
        )

    @staticmethod
    def validate(nonce: str,
                 difficulty: int,
                 response: int,
                 ) -> bool:
        """
        Validate a proof of work response.
        :param nonce: The nonce used for the proof of work challenge.
        :param difficulty: How many leading zeros the hash should have.
        :param response: The response to validate against the challenge.
        :return: True if the response is valid, False otherwise.
        """
        data = f'{nonce}{response}'.encode()
        h = hashlib.sha256(data).hexdigest()
        bin_hash = bin(int(h, 16))[2:].zfill(256)

        target = '0' * difficulty

        return bin_hash.startswith(target)
