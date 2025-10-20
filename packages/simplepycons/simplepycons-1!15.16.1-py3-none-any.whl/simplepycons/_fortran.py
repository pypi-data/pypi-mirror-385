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


class FortranIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "fortran"

    @property
    def original_file_name(self) -> "str":
        return "fortran.svg"

    @property
    def title(self) -> "str":
        return "Fortran"

    @property
    def primary_color(self) -> "str":
        return "#734F96"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Fortran</title>
     <path d="M19.536 0H4.464A4.463 4.463 0 0 0 0 4.464v15.073A4.463
 4.463 0 0 0 4.464 24h15.073A4.463 4.463 0 0 0 24 19.536V4.464A4.463
 4.463 0 0 0 19.536 0zm1.193
 6.493v3.871l-.922-.005c-.507-.003-.981-.021-1.052-.041-.128-.036-.131-.05-.192-.839-.079-1.013-.143-1.462-.306-2.136-.352-1.457-1.096-2.25-2.309-2.463-.509-.089-2.731-.176-4.558-.177L10.13
 4.7v5.82l.662-.033c.757-.038 1.353-.129
 1.64-.252.306-.131.629-.462.781-.799.158-.352.262-.815.345-1.542.033-.286.07-.572.083-.636.024-.116.028-.117
 1.036-.117h1.012v9.3h-2.062l-.035-.536c-.063-.971-.252-1.891-.479-2.331-.311-.601-.922-.871-2.151-.95a11.422
 11.422 0 0 1-.666-.059l-.172-.027.02 2.926c.021 3.086.03 3.206.265
 3.465.241.266.381.284 2.827.368.05.002.065.246.065
 1.041v1.039H3.271v-1.039c0-.954.007-1.039.091-1.041.05-.001.543-.023
 1.097-.049.891-.042 1.033-.061 1.244-.167a.712.712 0 0 0
 .345-.328c.106-.206.107-.254.107-6.78
 0-6.133-.006-6.584-.09-6.737a.938.938 0 0
 0-.553-.436c-.104-.032-.65-.07-1.215-.086l-1.026-.027V2.622h17.458v3.871z"
 />
</svg>'''

    @property
    def guidelines_url(self) -> "str | None":
        _value: "str" = ''''''
        if len(_value) > 0:
            return _value
        return None

    @property
    def source(self) -> "str":
        return '''https://github.com/fortran-lang/fortran-lang.
org/blob/5469465d08d3fcbf16d048e651ca5c9ba050839c/assets/img/fortran-l'''

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
