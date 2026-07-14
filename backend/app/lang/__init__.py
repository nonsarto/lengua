"""Sprachpaket-Loader: APP_LANG=es (Default) | ca. Eine Codebasis, zwei Apps —
lengua (Spanisch) und llengua (Katalanisch) unterscheiden sich nur durch Konfiguration."""

import os


def get_lang():
    code = os.environ.get("APP_LANG", "es")
    if code == "ca":
        from . import ca
        return ca
    from . import es
    return es
