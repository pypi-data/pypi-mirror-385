#
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2025 Carsten Igel.
#
# This file is part of simplepycons
# (see https://github.com/carstencodes/simplepycons).
#
# This file is published using the MIT license.
# Refer to LICENSE for more information
#
""""""
# pylint: disable=C0302
# Justification: Code is generated

from typing import TYPE_CHECKING

from .base_icon import Icon

if TYPE_CHECKING:
    from collections.abc import Iterable


class UblockOriginIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "ublockorigin"

    @property
    def original_file_name(self) -> "str":
        return "ublockorigin.svg"

    @property
    def title(self) -> "str":
        return "uBlock Origin"

    @property
    def primary_color(self) -> "str":
        return "#800000"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>uBlock Origin</title>
     <path d="M12 0C7.502 3 6.002 3 1.5 3c0 15.002 0 15.002 10.5 21
 10.5-5.998 10.5-5.998 10.5-21-4.498 0-5.998 0-10.5-3zM5.956
 7.472h1.512v4.536c0 1.322.19 1.508 1.512 1.508 1.323 0 1.512-.19
 1.512-1.512V7.472H12v.767a3.75 3.75 0 012.268-.767 3.79 3.79 0
 013.776 3.78 3.79 3.79 0 01-3.78 3.775 3.765 3.764 0
 01-2.684-1.133c-.464.77-1.315 1.133-2.6 1.133-2.079
 0-3.024-.944-3.024-3.023zm8.308 1.512A2.254 2.254 0 0012 11.252a2.254
 2.254 0 002.268 2.264 2.254 2.254 0 002.264-2.268 2.254 2.254 0
 00-2.268-2.264z" />
</svg>'''

    @property
    def guidelines_url(self) -> "str | None":
        _value: "str" = ''''''
        if len(_value) > 0:
            return _value
        return None

    @property
    def source(self) -> "str":
        return '''https://github.com/gorhill/uBlock/blob/59aa23'''

    @property
    def license(self) -> "tuple[str | None, str | None]":
        _type: "str | None" = ''''''
        _url: "str | None" = ''''''

        if _type is not None and len(_type) == 0:
            _type = None

        if _url is not None and len(_url) == 0:
            _url = None

        return _type, _url

    @property
    def aliases(self) -> "Iterable[str]":
        yield from []
