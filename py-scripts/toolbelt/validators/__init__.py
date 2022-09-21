from toolbelt.client.notion import ReleaseNoteProperties


__all__ = ("validate",)


def validate(properties: ReleaseNoteProperties) -> bool:
    from . import apv

    return all(
        [
            apv.validate(properties),
        ]
    )
