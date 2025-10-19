import logging
import os
from typing import Iterator, Optional, TypeAlias, Union, cast

from dotenv import load_dotenv as dotenv_load_dotenv
from dotenv.parser import parse_stream, Binding
from win32.win32crypt import CryptProtectData, CryptUnprotectData  # pyright: ignore[reportUnknownVariableType]
from win32cryptcon import CRYPTPROTECT_UI_FORBIDDEN
from envencrypt.worker import fire_and_forget

logger = logging.getLogger(__name__)

# Define custom type aliases
ConfigDict: TypeAlias = dict[str, str]
EnvDict: TypeAlias = dict[str, str | None]
StrPath = Union[str, "os.PathLike[str]"]
ENC_PREFIX = "enc:"
DEFAULT_ENV_FILE = ".env"
ENCRYPTED_ENV_FILE = ".env.enc"
DEFAULT_ENCODING = "utf-8"

"""
CRYPTPROTECT_LOCAL_MACHINE : May fail after reboot, restore - need testing
"""


class EnvEncrypt:
    _env_raw: EnvDict = {}
    encrypted_dotenv_path: StrPath = ENCRYPTED_ENV_FILE
    bindings: list[Binding] = []
    lines: list[str] = []
    encoding: Optional[str] = DEFAULT_ENCODING

    def __init__(
        self,
        encrypted_dotenv_path: Optional[StrPath] = ENCRYPTED_ENV_FILE,
        verbose: bool = False,
        encoding: Optional[str] = DEFAULT_ENCODING,
        override: bool = True,
    ) -> None:
        self.override = override
        self.encoding = encoding
        self.encrypted_dotenv_path = encrypted_dotenv_path or ENCRYPTED_ENV_FILE
        self.read_encrypted_env_file()

    def read_encrypted_env_file(self) -> None:
        if not os.path.isfile(self.encrypted_dotenv_path):
            return
        f = open(
            self.encrypted_dotenv_path, "r", encoding=self.encoding or DEFAULT_ENCODING
        )
        bindings: Iterator[Binding] = parse_stream(f)
        for binding in bindings:
            self.bindings.append(binding)
        
        f.close()

    @staticmethod
    def _encrypt_env_key(key: str, value: str) -> tuple[str, Optional[str]]:
        _value: Union[str, None] = None
        try:
            _enc: bytes = cast(
                bytes,
                CryptProtectData(
                    value.encode("utf-8"),
                    key,
                    None,
                    None,
                    None,
                    CRYPTPROTECT_UI_FORBIDDEN,
                ),
            )  # type: bytes
            _value = ENC_PREFIX + _enc.hex()
        except Exception as e:
            logger.error(f"Failed to encrypt {key}: {e}")
            _value = None
        return key, _value

    @staticmethod
    def _decrypt_value(value: str):
        encrypted_data = bytes.fromhex(value)
        return CryptUnprotectData(encrypted_data)

    @staticmethod
    def encrypt_env(dotenv_path: StrPath, save: Union[bool, StrPath] = True) -> EnvDict:
        """
        Encrypts all the values in the given dotenv file and optionally saves the
        encrypted variables back to the file.
        Args:
            dotenv_path (StrPath): Path to the file to be encrypted.
            save (Union[bool, StrPath]): Whether to save the encrypted variables
            back to the file or to a specified path.
        Returns:
            EnvDict: A dictionary containing the encrypted environment variables.
        """
        encrypted_env: EnvDict = {}
        lines: list[str] = []
        f = open(dotenv_path, "r", encoding="utf-8")
        try:
            bindings: Iterator[Binding] = parse_stream(f)
            for binding in bindings:
                key = binding.key
                value = binding.value
                original = binding.original
                if key is None and value is None:
                    # preserve comments and blank lines
                    lines.append(original.string)
                elif key is not None and value is None:
                    # preserve keys without values
                    lines.append(original.string)
                    encrypted_env[key] = None
                elif key is not None and value is not None:
                    val: Union[str, None] = value
                    if len(value) == 0:
                        # preserve empty values
                        lines.append(f"{key}=\n")
                        encrypted_env[key] = ""
                        continue
                    # avoid double encryption by checking for ENC_PREFIX
                    if not value.startswith(ENC_PREFIX):
                        (_, enc_val) = EnvEncrypt._encrypt_env_key(key, value)
                        val = enc_val
                    encrypted_env[key] = val
                    lines.append(f"{key}={val}\n")
            f.close()
            if save is True or (isinstance(save, str) and len(save) > 0):
                _path = save if isinstance(save, str) else dotenv_path
                with open(_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
        except Exception as e:
            logger.error(f"Failed to encrypt env file {dotenv_path}: {e}")
        finally:
            f.close()
        return encrypted_env

    @staticmethod
    def decrypt_env(encrypted_env_path: StrPath) -> EnvDict:
        decrypted_env: EnvDict = {}
        f = open(encrypted_env_path, "r", encoding="utf-8")
        bindings: Iterator[Binding] = parse_stream(f)
        try:
            for binding in bindings:
                key = binding.key
                value = binding.value
                if key is not None and value is not None:
                    if value.startswith(ENC_PREFIX):
                        try:
                            decrypted_data = EnvEncrypt._decrypt_value(
                                value[len(ENC_PREFIX) :]
                            )
                            if len(decrypted_data[1]) > 6:
                                logger.debug(
                                    f"Decrypted {key}: {decrypted_data[1][:3]}..."
                                )
                            decrypted_env[key] = decrypted_data[1].decode("utf-8")
                        except Exception as e:
                            logger.error(f"Failed to decrypt {key}: {e}")
                            decrypted_env[key] = None
                    else:
                        decrypted_env[key] = value
                elif key is not None and value is None:
                    decrypted_env[key] = None
        except Exception as e:
            logger.error(f"Failed to decrypt env file {encrypted_env_path}: {e}")
        finally:
            f.close()
        return decrypted_env

    def set_env_variables(self) -> None:
        for binding in self.bindings:
            key = binding.key
            value = binding.value
            if key is not None and value is not None:
                if value.startswith(ENC_PREFIX):
                    try:
                        decrypted_data = self._decrypt_value(value[len(ENC_PREFIX) :])
                        if self.override or key not in os.environ:
                            os.environ[key] = decrypted_data[1].decode("utf-8")
                    except Exception as e:
                        logger.error(f"Failed to decrypt {key}: {e}")
                else:
                    if self.override or key not in os.environ:
                        os.environ[key] = value
            


def load_dotenve(
    dotenv_path: Optional[StrPath] = None,
    encrypted_dotenv_path: Optional[StrPath] = None,
    verbose: bool = False,
    override: bool = False,
    encrypt_override: bool = True,
    interpolate: bool = True,
    encoding: Optional[str] = "utf-8",
    encrypt_in_background: bool = True,
) -> bool:
    """
    Load environment variables from dotenv files and optionally encrypt them.

    This function loads environment variables from a standard .env file and can also
    work with encrypted dotenv files. It provides options for encryption, interpolation,
    and background processing.

    Args:
        dotenv_path (Optional[StrPath], optional): Path to the .env file to load.
            If None, uses default dotenv discovery. Defaults to None.
        encrypted_dotenv_path (Optional[StrPath], optional): Path to the encrypted
            dotenv file. If None, uses default encrypted file path. Defaults to .env.enc.
        verbose (bool, optional): Enable verbose output for debugging. Defaults to False.
        override (bool, optional): Whether to override existing environment variables
            when loading from dotenv. Defaults to False.
        encrypt_override (bool, optional): Whether to override existing environment
            variables when loading from encrypted dotenv. Defaults to True.
        interpolate (bool, optional): Enable variable interpolation in dotenv values.
            Defaults to True.
        encoding (Optional[str], optional): Text encoding for reading dotenv files.
            Defaults to "utf-8".
        encrypt_in_background (bool, optional): Whether to encrypt the dotenv file
            in the background asynchronously. Defaults to True.

    Returns:
        bool: True if the dotenv file was successfully loaded, False otherwise.
            The return value reflects the success of the dotenv loading operation.

    Note:
        When encrypt_in_background is True, the encryption process runs asynchronously
        and does not block the main execution flow.
    """
    result = dotenv_load_dotenv(
        dotenv_path=dotenv_path,
        verbose=verbose,
        interpolate=interpolate,
        override=override,
        encoding=encoding,
    )
    encrypted_env = EnvEncrypt(
        encrypted_dotenv_path=encrypted_dotenv_path,
        verbose=verbose,
        encoding=encoding,
        override=encrypt_override,
    )

    if encrypt_in_background is True:
        # Create an async wrapper to encrypt the dotenv file in background
        async def encrypt_dotenv_async():
                EnvEncrypt.encrypt_env(
                    encrypted_dotenv_path or ENCRYPTED_ENV_FILE,
                    save=True,
                )
                return True

        # Schedule the encryption in background
        fire_and_forget(encrypt_dotenv_async())

    encrypted_env.set_env_variables()
    return result



