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


class DaciaIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "dacia"

    @property
    def original_file_name(self) -> "str":
        return "dacia.svg"

    @property
    def title(self) -> "str":
        return "Dacia"

    @property
    def primary_color(self) -> "str":
        return "#646B52"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Dacia</title>
     <path d="M0 8.646v2.23h8.252v2.248H0v2.23h9.112a.62.62 0
 00.489-.201L12 12.819l2.399 2.334a.62.62 0
 00.49.201H24v-2.23h-8.252v-2.248H24v-2.23h-9.112a.62.62 0
 00-.489.201L12 11.181 9.601 8.847a.62.62 0 00-.49-.201Z" />
</svg>'''

    @property
    def guidelines_url(self) -> "str | None":
        _value: "str" = ''''''
        if len(_value) > 0:
            return _value
        return None

    @property
    def source(self) -> "str":
        return '''https://commons.wikimedia.org/wiki/File:Dacia'''

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
