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


class UnraidIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "unraid"

    @property
    def original_file_name(self) -> "str":
        return "unraid.svg"

    @property
    def title(self) -> "str":
        return "Unraid"

    @property
    def primary_color(self) -> "str":
        return "#F15A2C"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Unraid</title>
     <path d="M11.406 8.528h1.17v6.926h-1.17zM1.17
 15.454H0V8.528h1.17zm4.534.828h1.17v2.645h-1.17zm-2.86-2.969h1.169v4.282h-1.17zm5.703
 0h1.17v4.282h-1.17zM22.83
 8.528H24v6.926h-1.17zm-4.534-.81h-1.17V5.073h1.17zm2.86
 2.95h-1.169V6.406h1.17zm-5.72 0h-1.17V6.406h1.17z" />
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
