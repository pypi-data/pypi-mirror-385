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


class ReverbnationIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "reverbnation"

    @property
    def original_file_name(self) -> "str":
        return "reverbnation.svg"

    @property
    def title(self) -> "str":
        return "ReverbNation"

    @property
    def primary_color(self) -> "str":
        return "#E43526"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>ReverbNation</title>
     <path d="M24 9.324l-9.143-.03L11.971.57 9.143 9.294 0
 9.324h.031l7.367 5.355-2.855 8.749h.029l7.459-5.386 7.396
 5.386-2.855-8.73L24 9.315" />
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
