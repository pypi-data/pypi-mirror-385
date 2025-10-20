# modelred/__init__.py
__version__ = "0.1.37"


class ComingSoonError(RuntimeError):
    pass


def __getattr__(name):
    raise ComingSoonError(
        "ModelRed SDK — Coming Soon. This placeholder exposes no API yet."
    )
