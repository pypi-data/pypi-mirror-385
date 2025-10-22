# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""System Fields for Global Search records."""


from .context import GlobalSearchPIDFieldContext
from .original import OriginalField
from .providers import GlobalSearchRecordProvider

__all__ = ("GlobalSearchRecordProvider", "GlobalSearchPIDFieldContext", "OriginalField")
