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


class MicrostrategyIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "microstrategy"

    @property
    def original_file_name(self) -> "str":
        return "microstrategy.svg"

    @property
    def title(self) -> "str":
        return "MicroStrategy"

    @property
    def primary_color(self) -> "str":
        return "#D9232E"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>MicroStrategy</title>
     <path d="M9.095 2.572h5.827v18.856H9.096zM0
 2.572h5.825v18.856H.001zm18.174 0v18.854H24V8.33z" />
</svg>'''

    @property
    def guidelines_url(self) -> "str | None":
        _value: "str" = '''https://www.microstrategy.com/en/company/pres'''
        if len(_value) > 0:
            return _value
        return None

    @property
    def source(self) -> "str":
        return '''https://www.microstrategy.com/en/company/pres'''

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
