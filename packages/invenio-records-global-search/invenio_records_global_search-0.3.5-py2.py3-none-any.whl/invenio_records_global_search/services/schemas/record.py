# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search Schemas."""

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow.fields import Dict
from marshmallow_utils.fields import NestedAttribute

from .metadata import GlobalSearchMetadataSchema


class GlobalSearchRecordSchema(BaseRecordSchema):
    """GlobalSearchRecordSchema."""

    metadata = NestedAttribute(GlobalSearchMetadataSchema)

    original = Dict()
