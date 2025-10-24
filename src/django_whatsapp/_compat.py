import sys

if sys.version_info >= (3, 13):
    from typing import TypeIs
else:
    from typing_extensions import TypeIs

__all__ = [
    "TypeIs",
]
