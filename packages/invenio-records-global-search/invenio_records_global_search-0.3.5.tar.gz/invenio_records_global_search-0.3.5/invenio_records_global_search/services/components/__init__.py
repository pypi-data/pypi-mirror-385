# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Components."""


from invenio_records_resources.services.records.components import MetadataComponent

from .original import OriginalComponent

DefaultRecordsComponents = [
    MetadataComponent,
    OriginalComponent,
]


__all__ = ("DefaultRecordsComponents",)
