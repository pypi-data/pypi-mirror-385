# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search Metadata Schema."""

from marshmallow import Schema
from marshmallow.fields import List, String
from marshmallow_utils.fields import SanitizedUnicode


class GlobalSearchMetadataSchema(Schema):
    """GlobalSearchMetadataSchema."""

    contributors = List(String())
    titles = List(SanitizedUnicode(required=True))
    creators = List(String(required=True))
    identifiers = List(String(required=True))
    relations = List(String())
    rights = List(String())
    dates = List(String())
    subjects = List(String())
    descriptions = List(String())
    publishers = List(String())
    types = List(String())
    sources = List(String())
    languages = List(String())
    locations = List(String())
    formats = List(String())
