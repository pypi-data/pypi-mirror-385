# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

from .ext import InvenioRecordsGlobalSearch

current_records_global_search: LocalProxy[InvenioRecordsGlobalSearch] = LocalProxy(
    lambda: current_app.extensions["invenio-records-global-search"],
)
"""Helper proxy to get the global search extension."""
