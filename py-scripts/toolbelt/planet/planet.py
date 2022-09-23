import shutil
import subprocess
from typing import Optional, Tuple

from .apv import Apv

PLANET_CLI_PATH = shutil.which("planet")
assert PLANET_CLI_PATH is not None


class Planet:
    def __init__(self, executable: Optional[str] = PLANET_CLI_PATH) -> None:
        self._executable = executable

    def apv_analyze(self, apv: str) -> Apv:
        result = subprocess.run(
            ["planet", "apv", "analyze", apv], capture_output=True
        )
        if result.returncode:
            raise ValueError()

        output = result.stdout
        split = [x.decode("utf-8") for x in output.split()]
        properties = dict(
            (split[i], split[i + 1]) for i in range(0, len(split), 2)
        )
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

    def apv_sign(self, signer: Tuple[str, str], version: int, **kwargs) -> Apv:
        address, passphrase = signer

        key_id = self._get_key_id_v2(address)
        raw_command = (
            f"planet apv sign --passphrase {passphrase} {key_id} {version} "
        )

        for k, v in kwargs.items():
            raw_command += f"-e {k}={v} "

        out = subprocess.run(
            raw_command, capture_output=True, text=True, shell=True
        )
        if not out.stdout:
            raise Exception(out.stderr)
        return self.apv_analyze(out.stdout.strip())

    def _get_key_id_v2(self, address: str) -> str:
        out = subprocess.run(["planet", "key"], capture_output=True, text=True)
        keys = out.stdout.split()

        for i in range(0, len(keys), 2):
            out_key = keys[i]
            out_address = keys[i + 1]
            if out_address == address:
                return out_key

        raise ValueError(f"Failed to import APV key for {address}")
