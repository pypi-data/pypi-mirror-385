# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search PID context."""

from invenio_records_resources.records.systemfields.pid import PIDFieldContext


class GlobalSearchPIDFieldContext(PIDFieldContext):
    """GlobalSearchPIDFieldContext."""

    pid_type = "gs"
