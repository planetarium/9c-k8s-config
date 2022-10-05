from toolbelt.config import config
from toolbelt.planet import Planet

from .update_post_deploy import update_post_deploy

__all__ = [
    "update_post_deploy",
]

planet = Planet(config.key_address, config.key_passphrase)
