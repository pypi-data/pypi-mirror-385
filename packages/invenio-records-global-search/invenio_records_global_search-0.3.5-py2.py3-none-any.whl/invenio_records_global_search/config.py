# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Configs."""

from typing import Any

from invenio_i18n import gettext as _

from .services.facets import data_model, formats, publishers, rights, subjects, types

GLOBAL_SEARCH_FACETS: dict[str, dict[str, Any]] = {
    "data_model": {
        "facet": data_model,
        "ui": {
            "field": "original.schema",
        },
    },
    "subjects": {
        "facet": subjects,
        "ui": {
            "field": "metadata.subjects",
        },
    },
    "publishers": {
        "facet": publishers,
        "ui": {
            "field": "metadata.publishers",
        },
    },
    "formats": {
        "facet": formats,
        "ui": {
            "field": "metadata.formats",
        },
    },
    "rights": {
        "facet": rights,
        "ui": {
            "field": "metadata.rights",
        },
    },
    "types": {
        "facet": types,
        "ui": {
            "field": "metadata.types",
        },
    },
}

GLOBAL_SEARCH_SORT_OPTIONS = {
    "bestmatch": {
        "title": _("Best match"),
        "fields": ["_score"],  # search defaults to desc on `_score` field
    },
    "newest": {
        "title": _("Newest"),
        "fields": ["-created"],
    },
    "version": {
        "title": _("Version"),
        "fields": ["version_id"],
    },
}

GLOBAL_SEARCH_SEARCH = {
    "facets": ["data_model", "subjects", "publishers", "formats", "rights", "types"],
    "sort": [
        "bestmatch",
        "newest",
        "version",
    ],
}

GLOBAL_SEARCH_BASE_TEMPLATE = "invenio_records_global_search/base.html"

GLOBAL_SEARCH_ORIGINAL_SCHEMAS: dict[str, dict[str, str]] = {}
"""Configure the original schema names."""
