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


class HsbcIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "hsbc"

    @property
    def original_file_name(self) -> "str":
        return "hsbc.svg"

    @property
    def title(self) -> "str":
        return "HSBC"

    @property
    def primary_color(self) -> "str":
        return "#DB0011"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>HSBC</title>
     <path d="m24 12.007-5.996 5.997V5.996L24
 12.007zm-5.996-6.01H6.01l5.996 6.01 5.997-6.01zM0 12.006l6.01
 5.997V5.996L0 12.007zm6.01 5.997h11.994l-5.997-5.997-5.996 5.997z" />
</svg>'''

    @property
    def guidelines_url(self) -> "str | None":
        _value: "str" = ''''''
        if len(_value) > 0:
            return _value
        return None

    @property
    def source(self) -> "str":
        return ''''''

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
