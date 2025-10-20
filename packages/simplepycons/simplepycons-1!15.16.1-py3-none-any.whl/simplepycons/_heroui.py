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


class HerouiIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "heroui"

    @property
    def original_file_name(self) -> "str":
        return "heroui.svg"

    @property
    def title(self) -> "str":
        return "HeroUI"

    @property
    def primary_color(self) -> "str":
        return "#000000"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>HeroUI</title>
     <path d="M6.353 0h11.294A6.353 6.353 0 0 1 24 6.353v11.294A6.353
 6.353 0 0 1 17.647 24H6.353A6.353 6.353 0 0 1 0 17.647V6.353A6.353
 6.353 0 0 1 6.353 0Zm7.755 6.913h-.933v6.702a2.88 2.88 0 0 1-.362
 1.45c-.24.424-.596.77-1.025 1-.443.244-.96.365-1.553.365-.592
 0-1.108-.121-1.55-.364a2.603 2.603 0 0 1-1.024-1 2.865 2.865 0 0
 1-.365-1.45V6.912h-.933v6.767a3.558 3.558 0 0 0 .489
 1.862c.327.547.798.994 1.362 1.292.582.316 1.256.474 2.021.474.769 0
 1.444-.157 2.024-.471a3.473 3.473 0 0 0
 1.36-1.293c.33-.565.5-1.21.49-1.864V6.913Zm3.648
 10.22V6.914h-.933v10.22h.933Z" />
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
