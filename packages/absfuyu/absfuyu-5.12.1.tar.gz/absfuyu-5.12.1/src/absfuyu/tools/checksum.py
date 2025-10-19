"""
Absufyu: Checksum
-----------------
Check MD5, SHA256, ...

Version: 5.12.0
Date updated: 17/10/2025 (dd/mm/yyyy)
"""

# Module level
# ---------------------------------------------------------------------------
__all__ = ["Checksum", "ChecksumMode"]


# Library
# ---------------------------------------------------------------------------
import hashlib
from enum import StrEnum
from pathlib import Path
from typing import Literal

from absfuyu.core.baseclass import BaseClass
from absfuyu.core.docstring import deprecated, versionadded, versionchanged
from absfuyu.core.dummy_func import tqdm


# Function
# ---------------------------------------------------------------------------
@deprecated("5.0.0")
def _checksum_operation(
    file: Path | str,
    hash_mode: str | Literal["md5", "sha1", "sha256", "sha512"] = "sha256",
) -> str:
    """
    This performs checksum
    """
    if hash_mode.lower() == "md5":
        hash_engine = hashlib.md5()
    elif hash_mode.lower() == "sha1":
        hash_engine = hashlib.sha1()
    elif hash_mode.lower() == "sha256":
        hash_engine = hashlib.sha256()
    elif hash_mode.lower() == "sha512":
        hash_engine = hashlib.sha512()
    else:
        hash_engine = hashlib.md5()

    with open(Path(file), "rb") as f:
        while True:
            data = f.read(4096)
            if len(data) == 0:
                break
            else:
                hash_engine.update(data)
    return hash_engine.hexdigest()


# Class
# ---------------------------------------------------------------------------
class ChecksumMode(StrEnum):
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"


@versionchanged("4.1.1", reason="Checksum for entire folder is possible")
@versionadded("4.1.0")
class Checksum(BaseClass):
    """
    Checksum engine

    Parameters
    ----------
    path : str | Path
        Path to file/directory to perform checksum

    hash_mode : ChecksumMode | Literal["md5", "sha1", "sha256", "sha512"], optional
        Hash mode, by default ``"sha256"``

    save_result_to_file : bool, optional
        Save checksum result(s) to file, by default ``False``
    """

    def __init__(
        self,
        path: str | Path,
        hash_mode: (
            ChecksumMode | Literal["md5", "sha1", "sha256", "sha512"]
        ) = ChecksumMode.SHA256,
        save_result_to_file: bool = False,
    ) -> None:
        """
        Checksum engine

        Parameters
        ----------
        path : str | Path
            Path to file/directory to perform checksum

        hash_mode : ChecksumMode | Literal["md5", "sha1", "sha256", "sha512"], optional
            Hash mode, by default ``"sha256"``

        save_result_to_file : bool, optional
            Save checksum result(s) to file, by default ``False``
        """
        self.path = Path(path)
        self.hash_mode = hash_mode
        self.save_result_to_file = save_result_to_file
        self.checksum_result_file_name = "checksum_results.txt"

    def _get_hash_engine(self):
        hash_mode = self.hash_mode
        if hash_mode.lower() == "md5":
            hash_engine = hashlib.md5()
        elif hash_mode.lower() == "sha1":
            hash_engine = hashlib.sha1()
        elif hash_mode.lower() == "sha256":
            hash_engine = hashlib.sha256()
        elif hash_mode.lower() == "sha512":
            hash_engine = hashlib.sha512()
        else:
            hash_engine = hashlib.md5()
        return hash_engine

    def _checksum_operation(
        self,
        file: Path | str,
    ) -> str:
        """This performs checksum"""

        hash_engine = self._get_hash_engine().copy()
        with open(Path(file), "rb") as f:
            # Read and hash the file in 4K chunks. Reading the whole
            # file at once might consume a lot of memory if it is
            # large.
            while True:
                data = f.read(4096)
                if len(data) == 0:
                    break
                else:
                    hash_engine.update(data)
        return hash_engine.hexdigest()  # type: ignore

    def checksum(self, recursive: bool = True) -> str:
        """
        Perform checksum

        Parameters
        ----------
        recursive : bool, optional
            Do checksum for every file in the folder (including child folder),
            by default ``True``

        Returns
        -------
        str
            Checksum hash
        """
        if self.path.absolute().is_dir():  # Dir
            new_path = self.path.joinpath(self.checksum_result_file_name)
            # List of files
            if recursive:
                file_list: list[Path] = [
                    x for x in self.path.glob("**/*") if x.is_file()
                ]
            else:
                file_list = [x for x in self.path.glob("*") if x.is_file()]

            # Checksum
            res = []
            for x in tqdm(file_list, desc="Calculating hash", unit_scale=True):
                name = x.relative_to(self.path)
                res.append(f"{self._checksum_operation(x)} | {name}")
            output = "\n".join(res)
        else:  # File
            new_path = self.path.with_name(self.checksum_result_file_name)
            output = self._checksum_operation(self.path)

        # Save result
        if self.save_result_to_file:
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(output)

        return output
