# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Records API."""

from invenio_records.systemfields import ConstantField, DictField
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField, PIDField
from typing_extensions import Self

from .models import GlobalSearchMetadata
from .systemfields import (
    GlobalSearchPIDFieldContext,
    GlobalSearchRecordProvider,
    OriginalField,
)


class GlobalSearchRecord(Record):
    """Dublin Core Record."""

    model_cls = GlobalSearchMetadata

    schema = ConstantField(
        "$schema",
        "local://global-search/records/global-search-record-v1.0.0.json",
    )

    index = IndexField(
        "global-search-records-record-v1.0.0",
        search_alias="global-search",
    )

    pids = DictField("pids")

    pid = PIDField(
        key="id",
        create=True,
        provider=GlobalSearchRecordProvider,
        context_cls=GlobalSearchPIDFieldContext,
    )

    original = OriginalField()

    gs_pid = None

    @classmethod
    def create(cls, data: dict, id_: str | None = None, **kwargs: dict) -> Self:
        """Create."""
        data["gs_pid"] = cls.gs_pid
        return super().create(data, id_, **kwargs)
