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


class InstatusIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "instatus"

    @property
    def original_file_name(self) -> "str":
        return "instatus.svg"

    @property
    def title(self) -> "str":
        return "Instatus"

    @property
    def primary_color(self) -> "str":
        return "#4EE3C2"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Instatus</title>
     <path d="m16.994 21.028c3.5843-1.91 5.471-5.759
 5.0561-9.5637-1.3206 1.0851-2.6237 2.3203-3.8709 3.6906-2.0656
 2.2694-3.7476 4.6559-4.9953 6.9817 1.2946-0.09715 2.5907-0.45868
 3.8101-1.1086zm-13.394-2.5626c-1.3408 1.8191-2.3771 4.4991-1.3032
 5.3066 1.5151 1.1394 8.404-2.0133 13.908-8.8051 5.504-6.7918
 7.3265-13.796 4.879-14.873-1.1283-0.49644-3.486 1.083-4.8394
 2.3943l0.58412 0.31415c1.332-0.85276 3.5528-1.7338 1.4995
 1.9758-0.0097 0.01768-0.01962 0.03541-0.02949
 0.05317-2.9067-2.2075-6.9471-2.662-10.379-0.8328-4.7026 2.506-6.4831
 8.3499-3.9771 13.052 0.58979 1.1067 1.3644 2.0516 2.2655
 2.8168-3.5586 2.7493-2.6905 0.35965-2.1925-0.8162z" />
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
