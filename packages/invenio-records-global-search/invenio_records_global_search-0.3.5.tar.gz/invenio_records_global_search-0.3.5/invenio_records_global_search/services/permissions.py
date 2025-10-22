# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search permission policy."""
from typing import ClassVar

from invenio_records_permissions.generators import AnyUser, RecordOwners, SystemProcess
from invenio_records_permissions.policies.records import RecordPermissionPolicy


class GlobalSearchRecordPermissionPolicy(RecordPermissionPolicy):
    """GlobalSearchRecordPermissionPolicy."""

    can_create: ClassVar = [AnyUser(), SystemProcess()]

    can_search: ClassVar = [AnyUser(), SystemProcess()]
    can_read: ClassVar = [AnyUser(), RecordOwners()]

    can_update: ClassVar = [AnyUser(), SystemProcess()]
