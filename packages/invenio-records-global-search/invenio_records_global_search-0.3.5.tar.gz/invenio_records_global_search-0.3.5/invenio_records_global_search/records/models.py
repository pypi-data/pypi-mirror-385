# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dublin Core database models."""


from invenio_db import db
from invenio_records.models import RecordMetadataBase


class GlobalSearchMetadata(db.Model, RecordMetadataBase):
    """Base class for global search records."""

    __tablename__ = "global_search_metadata"
