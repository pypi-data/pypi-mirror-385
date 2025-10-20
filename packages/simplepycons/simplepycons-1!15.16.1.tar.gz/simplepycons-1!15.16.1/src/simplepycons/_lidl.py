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


class LidlIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "lidl"

    @property
    def original_file_name(self) -> "str":
        return "lidl.svg"

    @property
    def title(self) -> "str":
        return "Lidl"

    @property
    def primary_color(self) -> "str":
        return "#0050AA"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Lidl</title>
     <path d="M0
 0v24h24V0zm.209.209h23.582v23.582H.209zm11.789.625C5.83.834.83
 5.834.83 12.002c0 6.168 5 11.168 11.168 11.168 6.167 0 11.167-5
 11.168-11.166C23.165 5.837 18.166.837 12 .834zm.002.709c5.777 0 10.46
 4.682 10.46 10.459v.004c-.004 5.773-4.686 10.452-10.46 10.453-5.777
 0-10.46-4.68-10.46-10.457C1.54 6.225 6.222 1.543 12 1.543zM9.229
 7.85c-.645 0-1.166.521-1.166 1.166v.004c0 1.044 1.261 1.567
 1.999.829.738-.738.215-2-.829-1.999zM2.73
 10.059v.71h.551v2.465h-.55v.713h4.644v-.65l.537-.54 1.486
 1.491-.55.547.357.36 2.973-2.977v-.713l-.826.83-1.848-1.848-2.129
 2.133v-.576l-1.904 1.06V10.77h.549v-.711zm8.905
 0v.71h.549v2.465h-.555v.713h3.129c2.325 0
 2.355-3.888.008-3.888zm4.963
 0v.71h.55v2.465h-.55v.713h4.648v-1.943l-1.906
 1.06V10.77h.55v-.711zm-2.43 1.21h.133c.687 0 .685 1.461.023
 1.461h-.156v-1.46z" />
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
