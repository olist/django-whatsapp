import sys

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


__all__ = [
    "override",
]
