# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search Service Config."""

from typing import ClassVar

from invenio_indexer.api import RecordIndexer
from invenio_records_resources.services import (
    RecordServiceConfig,
    SearchOptions,
    pagination_links,
)
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    FromConfigSearchOptions,
    SearchOptionsMixin,
)

from ..records import GlobalSearchRecord
from .components import DefaultRecordsComponents
from .facets import data_model, formats, publishers, rights, subjects, types
from .permissions import GlobalSearchRecordPermissionPolicy
from .schemas import GlobalSearchRecordSchema


class GlobalSearchSearchOptions(SearchOptions, SearchOptionsMixin):
    """Search options for record search."""

    facets: ClassVar = {
        "data_model": data_model,
        "subjects": subjects,
        "publishers": publishers,
        "formats": formats,
        "rights": rights,
        "types": types,
    }


class GlobalSearchRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Dublin Core record service config class."""

    record_cls = GlobalSearchRecord

    indexer_cls = RecordIndexer
    indexer_queue_name = "global-search-records"

    schema = FromConfig(
        "GLOBAL_SEARCH_SCHEMA",
        default=GlobalSearchRecordSchema,
    )

    permission_policy_cls = FromConfig(
        "GLOBAL_SEARCH_PERMISSION_POLICY",
        default=GlobalSearchRecordPermissionPolicy,
    )

    links_search = pagination_links("{+api}/global-search{?args*}")

    # Search
    search = FromConfigSearchOptions(
        "GLOBAL_SEARCH_SEARCH",
        "GLOBAL_SEARCH_SORT_OPTIONS",
        "GLOBAL_SEARCH_FACETS",
        search_option_cls=GlobalSearchSearchOptions,
    )

    components = FromConfig(
        "GLOBAL_SEARCH_RECORDS_SERVICE_COMPONENTS",
        default=DefaultRecordsComponents,
    )
