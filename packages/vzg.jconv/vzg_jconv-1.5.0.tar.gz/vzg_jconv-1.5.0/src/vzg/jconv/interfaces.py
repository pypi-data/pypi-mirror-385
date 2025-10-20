# -*- coding: UTF-8 -*-
"""Interfaces
##############################################################################
#
# Copyright (c) 2020-2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from zope.interface import Attribute, Interface

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"


class IArticle(Interface):
    """VZG Article"""

    journal = Attribute("Journal")
    json = Attribute("Article as JSON object")
    lang_code = Attribute("Language Code")
    primary_id = Attribute("Primäre ID des Datensatzes in der Datenquelle")
    title = Attribute("Article Title")


class IArchive(Interface):
    """Exchange Container"""

    converters = Attribute("List of IConverter objects")


class IConverter(Interface):
    """Converter"""

    articles = Attribute("List of IArticle objects")
    name = Attribute("Optional name of the source file")

    def run(self):
        """Start the conversion"""


class IJournal(Interface):
    """Journal"""

    def as_dict(self):
        """Dict representation"""

    journal_ids = Attribute("List of journal identifier")
    title = Attribute("Journal title")
    year = Attribute("Year")
