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


class PackerIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "packer"

    @property
    def original_file_name(self) -> "str":
        return "packer.svg"

    @property
    def title(self) -> "str":
        return "Packer"

    @property
    def primary_color(self) -> "str":
        return "#02A8EF"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Packer</title>
     <path d="M7.844 0v3.38l5.75 3.32v10.148l2.705 1.552c1.676.967
 3.045.388 3.045-1.285V9.668c-.014-1.687-1.382-3.832-3.059-4.799L7.844
 0zM4.656 2.932v16.574L12.436 24V7.426l-7.78-4.494Z" />
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
