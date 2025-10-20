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


class HiveBlockchainIcon(Icon):
    """"""
    @property
    def name(self) -> "str":
        return "hive_blockchain"

    @property
    def original_file_name(self) -> "str":
        return "hive_blockchain.svg"

    @property
    def title(self) -> "str":
        return "Hive"

    @property
    def primary_color(self) -> "str":
        return "#E31337"

    @property
    def raw_svg(self) -> "str":
        return ''' <svg xmlns="http://www.w3.org/2000/svg"
 role="img" viewBox="0 0 24 24">
    <title>Hive</title>
     <path d="M6.076 1.637a.103.103 0 00-.09.05L.014 11.95a.102.102 0
 000 .104l6.039 10.26c.04.068.14.068.18 0l5.972-10.262a.102.102 0
 00-.002-.104L6.166 1.687a.103.103 0 00-.09-.05zm2.863 0c-.079
 0-.13.085-.09.154l5.186 8.967a.105.105 0 00.09.053h3.117c.08 0
 .13-.088.09-.157l-5.186-8.966a.104.104 0 00-.09-.051H8.94zm5.891
 0a.102.102 0 00-.088.154L20.656 12l-5.914 10.209a.102.102 0
 00.088.154h3.123a.1.1 0 00.088-.05l5.945-10.262a.1.1 0
 000-.102L18.041 1.688a.1.1 0 00-.088-.051H14.83zm-.79 11.7a.1.1 0
 00-.089.052l-5.101 8.82c-.04.069.01.154.09.154h3.117a.104.104 0
 00.09-.05l5.1-8.82a.103.103 0 00-.09-.155h-3.118z" />
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


class HiveIcon1(HiveBlockchainIcon):
    """HiveIcon1 is an alternative implementation name for HiveBlockchainIcon. 
          It is deprecated and may be removed in future versions."""
    def __init__(self, *args, **kwargs) -> "None":
        import warnings
        warnings.warn("The usage of 'HiveIcon1' is discouraged and may be removed in future major versions. Use 'HiveBlockchainIcon' instead.", DeprecationWarning)
        super().__init__(*args, **kwargs)

