# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search PID providers."""

from typing import Self

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2


class GlobalSearchRecordProvider(RecordIdProviderV2):
    """GlobalSearchRecordProvider."""

    pid_type = "gs"

    @classmethod
    def generate_id(cls, _: dict | None = None) -> str:
        """Generate id."""
        return cls.gs_pid

    @classmethod
    def create(
        cls,
        object_type: str | None = None,
        object_uuid: str | None = None,
        options: dict | None = None,
        **kwargs: dict,
    ) -> Self:
        """Create."""
        cls.gs_pid = kwargs["record"]["gs_pid"]
        return super().create(object_type, object_uuid, options, **kwargs)
