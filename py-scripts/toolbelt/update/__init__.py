from toolbelt.config import KEY_ADDRESS, KEY_PASSPHRASE
from toolbelt.planet import Planet

from .update_post_deploy import update_post_deploy

__all__ = [
    "update_post_deploy",
]

planet = Planet(KEY_ADDRESS, KEY_PASSPHRASE)
