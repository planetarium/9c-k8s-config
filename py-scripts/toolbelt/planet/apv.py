import abc
import getpass
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional

from toolbelt.config import INTERNAL_ADDRESS, MAINNET_ADDRESS

__all__ = (
    "Apv",
    "ApvParser",
    "Planet",
    "ApvParseError",
)


PLANET_CLI_PATH = shutil.which("planet")
assert PLANET_CLI_PATH is not None


class ApvParseError(Exception):
    ...


@dataclass(frozen=True)
class Apv:
    version: int
    signature: str
    signer: str
    extra: Dict[str, str]

    raw: str


class ApvParser(abc.ABC):
    @abc.abstractmethod
    def analyze_apv(self, apv: str) -> Apv:
        ...


class Planet(ApvParser):
    def __init__(self, executable: Optional[str] = PLANET_CLI_PATH) -> None:
        self._executable = executable

    def analyze_apv(self, apv: str) -> Apv:
        result = subprocess.run(["planet", "apv", "analyze", apv], capture_output=True)
        if result.returncode:
            raise ApvParseError()

        output = result.stdout
        split = [x.decode("utf-8") for x in output.split()]
        properties = dict((split[i], split[i + 1]) for i in range(0, len(split), 2))
        extra = dict(
            (key[6:], value)
            for key, value in properties.items()
            if key.startswith("extra.")
        )
        return Apv(
            int(properties["version"]),
            properties["signature"],
            properties["signer"],
            extra,
            apv,
        )

    def _get_key_id(self, nc_network: str) -> str:
        assert nc_network == "main" or nc_network == "internal", f"{nc_network}"

        out = subprocess.run(["planet", "key"], capture_output=True, text=True)
        key_address = out.stdout.split()
        for i in range(0, len(key_address), 2):
            key_id = key_address[i]
            address = key_address[i + 1]
            if (nc_network == "main" and address == MAINNET_ADDRESS) or (
                nc_network == "internal" and address == INTERNAL_ADDRESS
            ):
                return key_id

        raise Exception(f"Failed to import APV key for {nc_network}")

    def sign_apv(self, nc_network: str, version: int, timestamp: str) -> Apv:
        assert nc_network == "main" or nc_network == "internal", f"{nc_network}"

        key_id = self._get_key_id(nc_network)
        passphrase = getpass.getpass(f"Passphrase (of {key_id}): ")
        command_str = (
            f"planet apv sign --passphrase {passphrase} {key_id} {version} "
            f"-e WindowsBinaryUrl=https://download.nine-chronicles.com/v{version}/Windows.zip "
            f"-e timestamp={timestamp}"
        )
        out = subprocess.run(command_str, capture_output=True, text=True, shell=True)
        if not out.stdout:
            raise Exception(out.stderr)
        return self.analyze_apv(out.stdout.strip())

    def sign_apv_v2(
        self,
        passphrase: str,
        nc_network: str,
        version: int,
        timestamp: str,
        launcher_sha: str,
        player_sha: str,
    ) -> Apv:
        assert nc_network == "main" or nc_network == "internal", f"{nc_network}"

        key_id = self._get_key_id(nc_network)
        command_str = (
            f"planet apv sign --passphrase {passphrase} {key_id} {version} "
            f"-e launcher={launcher_sha} "
            f"-e player={player_sha} "
            f"-e timestamp={timestamp}"
        )
        out = subprocess.run(command_str, capture_output=True, text=True, shell=True)
        if not out.stdout:
            raise Exception(out.stderr)
        return self.analyze_apv(out.stdout.strip())
