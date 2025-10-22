"""
This module contains non gui Qt based components
"""

import contextlib
import os.path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from napari.settings import NapariSettings


def napari_get_settings(path=None) -> "NapariSettings":
    from napari.utils import theme  # noqa: PLC0415 I001
    from napari.settings import get_settings as _napari_get_settings  # noqa: PLC0415

    del theme  # skipcq: PTC-W0043
    # Need to import theme before settings to work around the circular import
    # error in napari==0.6.5.
    if path is not None:
        path = os.path.join(path, "settings.yaml")
    if path is not None:
        with contextlib.suppress(Exception):
            return _napari_get_settings(path)
    return _napari_get_settings()


__all__ = ("napari_get_settings",)
