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


class HTwoDatabaseIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "h2database"

    @property
    def original_file_name(self) -> "str":
        return "h2database.svg"

    @property
    def title(self) -> "str":
        return "H2 Database"

    @property
    def primary_color(self) -> "str":
        return "#09476B"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>H2 Database</title>
     <path d="M17.17 13.27c.14-.015.28-.023.416-.023.7 0 1.228.159
 1.599.469.37.314.555.756.555 1.334a2.861 2.861 0 0 1-.43
 1.455c-.291.492-.775 1.066-1.46 1.727-.453.446-1.061.976-1.821
 1.592a48.02 48.02 0 0 1-2.275
 1.742v2.083h9.895V21.24H17.99c.219-.159.59-.435 1.11-.832.519-.4
 1.033-.835 1.55-1.311.817-.76 1.425-1.5 1.822-2.215a4.624 4.624 0 0 0
 .597-2.268c0-1.213-.416-2.154-1.247-2.815-.828-.662-2.033-.994-3.613-.994-.344
 0-.692.015-1.036.049V6.04H13.86v4.701H8.965V6.04H5.65v12.846h3.315v-5.661h4.89v5.661h.039c.31-.242.623-.487.933-.74a28.564
 28.564 0 0 0 1.826-1.588 14.854 14.854 0 0 0 .517-.529zM12.011
 23.3A11.327 11.327 0 0 1 .7 11.99 11.305 11.305 0 0 1
 12.011.699a11.286 11.286 0 0 1 11.29 11.29v.351H24v-.351A11.985
 11.985 0 0 0 12.011 0 12.008 12.008 0 0 0 0 11.989 12.026 12.026 0 0
 0 12.011 24h.352v-.7z" />
</svg>'''

    @property
    def guidelines_url(self) -> "str | None":
        _value: "str" = ''''''
        if len(_value) > 0:
            return _value
        return None

    @property
    def source(self) -> "str":
        return '''https://github.com/h2database/h2database/blob
/4472d76fc6a77cb079a8a0c24d80dc05dade56e1/h2/src/docsrc/images/h2_v2_3'''

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
