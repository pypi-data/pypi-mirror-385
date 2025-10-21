# -*- coding: utf-8 -*-
import os
import sys
import base64
import string
import asyncio
import importlib
import traceback
import subprocess
from types import ModuleType
from typing import TypeVar, Generic, Optional
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, CipherContext
from eastwind.lib.path import DIR_ROOT, DIR_EASTWIND

BUILTIN_PREFIX: str = 'eastwind.modules.'
PROJECT_PREFIX: str = 'modules.'
# Check whether is in debugging mode.
DEBUG_MODE: bool = os.environ.get("EASTWIND_DEBUG") == "1"


def response(code: int = 200, **results) -> dict:
    """
    Generate a standard dictionary response with "code" and "results" keys.
    :param code: The code to be returned, generally it have the same means of the standard HTTP response code.
    :param results: Any results to be packed within the dictionary.
    :return: Packed JSON dictionary response.
    """
    if len(results) == 0:
        return { 'code': code }
    return { 'code': code, 'result': results }


def err(code: int, msg: str) -> dict:
    return { 'code': code, 'error': msg }


T = TypeVar('T')


class Result(Generic[T]):
    def __init__(self, value: Optional[T] = None, error: Optional[dict] = None):
        # Treat has error.
        if error is not None and value is not None:
            raise ValueError("result and error are mutually exclusive")
        # Save the result and error result.
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return not self.is_error()

    def is_error(self) -> bool:
        return isinstance(self.error, dict)


def is_hex_str(data: str) -> bool:
    return all(c in string.hexdigits for c in data)


def is_n_long_hex_str(data: str, length: int) -> bool:
    return len(data) == length and is_hex_str(data)


def is_32_bytes_hash(data: str) -> bool:
    return is_n_long_hex_str(data, 64)


def str_to_base64(raw: str) -> str:
    return base64.urlsafe_b64encode(raw.encode('utf-8')).decode('utf-8')


def base64_to_str(encoded: str) -> str:
    return base64.urlsafe_b64decode(encoded.encode('utf-8')).decode('utf-8')


def sm3_hash_text(text: str) -> bytes:
    digest: hashes.Hash = hashes.Hash(hashes.SM3())
    digest.update(text.encode('utf-8'))
    return digest.finalize()


def sm4_encrypt_cbc(plain_text: str, key: bytes, iv: bytes) -> str:
    # Prepare the raw data with padding.
    padder = padding.PKCS7(128).padder()
    padded_plain: bytes = padder.update(plain_text.encode('utf-8')) + padder.finalize()
    # Encrypt the data.
    cipher: Cipher = Cipher(algorithms.SM4(key), modes.CBC(iv))
    gen: CipherContext = cipher.encryptor()
    return (gen.update(padded_plain) + gen.finalize()).hex()


def sm4_decrypt_cbc(cipher_hex: str, key: bytes, iv: bytes) -> str:
    # Decrypt the data first.
    if not is_hex_str(cipher_hex):
        raise ValueError("cipher string must be hex string")
    cipher: Cipher = Cipher(algorithms.SM4(key), modes.CBC(iv))
    gen: CipherContext = cipher.decryptor()
    decrypted_data: bytes = gen.update(bytes.fromhex(cipher_hex)) + gen.finalize()
    # Un-pad the data.
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(decrypted_data) + unpadder.finalize()).decode('utf-8')


def import_module(module_name: str) -> ModuleType | None:
    # Load the modules to the running process.
    try:
        return importlib.import_module(module_name)
    # When fail to load the modules, return a None instead.
    except ModuleNotFoundError as e:
        return None
    except (ImportError, Exception):
        print(f"Error occurs during import of module '{module_name}': \n{traceback.format_exc()}")
        return None


def config_python_environ(env: dict) -> None:
    # Set encoding to UTF-8.
    env['PYTHONIOENCODING'] = 'UTF-8'
    # Add project directory to PATH.
    python_paths: list[str] = list({DIR_ROOT, os.path.dirname(DIR_EASTWIND)})
    env['PYTHONPATH'] = os.pathsep.join(python_paths)


def run_python_sync(*args, stdout=None, stderr=None) -> subprocess.Popen:
    # Configure the Python running environment.
    script_env = os.environ.copy()
    config_python_environ(script_env)
    # Launch the normal subprocess Popen method.
    proc = subprocess.Popen(
        [sys.executable, *args],
        cwd=os.getcwd(),
        env=script_env,
        stdout=stdout,
        stderr=stderr)
    proc.communicate()
    return proc


async def launch_python(*args, stdout=None, stderr=None) -> asyncio.subprocess.Process:
    # Configure the Python running environment.
    script_env = os.environ.copy()
    config_python_environ(script_env)
    # Launch the asyncio subprocess exec method.
    return await asyncio.create_subprocess_exec(
        sys.executable, *args,
        cwd=os.getcwd(),
        env=script_env,
        stdout=stdout,
        stderr=stderr,
    )


async def run_python(*args, stdout=None, stderr=None) -> asyncio.subprocess.Process:
    # Launch the asyncio subprocess exec method.
    proc = await launch_python(*args,
        stdout=stdout,
        stderr=stderr,
    )
    await proc.wait()
    return proc
