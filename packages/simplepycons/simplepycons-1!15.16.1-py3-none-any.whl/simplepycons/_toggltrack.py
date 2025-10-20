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


class TogglTrackIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "toggltrack"

    @property
    def original_file_name(self) -> "str":
        return "toggltrack.svg"

    @property
    def title(self) -> "str":
        return "Toggl Track"

    @property
    def primary_color(self) -> "str":
        return "#E57CD8"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Toggl Track</title>
     <path d="M12 0a12 12 0 1 0 0 24 12 12 0 0 0 0-24zm-.883
 4.322h1.766v8.757h-1.766zm-.74 2.053v1.789a4.448 4.448 0 1 0 3.247
 0V6.375a6.146 6.146 0 1 1-5.669 10.552 6.145 6.145 0 0 1
 2.421-10.552z" />
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
