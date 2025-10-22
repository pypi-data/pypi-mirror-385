# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dublin Core data model for InvenioRDM."""

from .ext import InvenioRecordsGlobalSearch
from .proxies import current_records_global_search
from .records import GlobalSearchRecord

__version__ = "0.3.5"

__all__ = (
    "__version__",
    "InvenioRecordsGlobalSearch",
    "GlobalSearchRecord",
    "current_records_global_search",
)
