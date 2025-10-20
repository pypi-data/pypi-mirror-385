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


class EboxIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "ebox"

    @property
    def original_file_name(self) -> "str":
        return "ebox.svg"

    @property
    def title(self) -> "str":
        return "EBOX"

    @property
    def primary_color(self) -> "str":
        return "#BE2323"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>EBOX</title>
     <path d="m.939 14.973 10.97 6.4V24L.94 17.6v-2.626zm22.123
 0v2.626l-10.971 6.4v-2.626l10.97-6.401ZM.939 10.66l10.97
 6.4v2.627l-7.223-4.214-1.068.622-2.253-1.313
 1.07-.623-1.496-.873V10.66zm22.123 0v2.626l-1.496.873 1.07.624-2.253
 1.313-1.07-.623-7.224 4.214V17.06l10.972-6.4ZM.939 6.347l10.97
 6.4v2.627l-3.525-2.057-1.067.622-2.252-1.314
 1.067-.622-1.429-.833-1.066.622-2.253-1.314
 1.068-.622-1.514-.883Zm22.123 0v2.626l-1.514.883 1.07.622-2.254
 1.315-1.068-.623-1.428.833 1.068.622-2.252 1.314-1.07-.622-3.525
 2.057v-2.627l10.972-6.4ZM12 8.584l3.236 1.885-2.252
 1.314-.983-.573-.982.573-2.252-1.314 3.235-1.885Zm0-4.293 6.916
 4.03-2.252 1.315L12 6.918 7.338 9.635 5.085 8.321ZM12 0l10.597
 6.175-2.252 1.314L12 2.627 3.657 7.489 1.405 6.175 12 0Z" />
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
