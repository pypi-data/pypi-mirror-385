# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Global Search Record Resource schema."""

from flask import current_app
from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.html import strip_html


class StrippedHTMLList(fields.List):
    """List field which strips HTML entities.

    The value is stripped using the bleach library. Any already
    escaped value is being unescaped before return.
    """

    def __init__(self, attribute: str) -> None:
        """Initialize field."""
        super().__init__(cls_or_instance=fields.Raw, attribute=attribute)

    def _serialize(  # type: ignore[override]
        self,
        value: list,
        attr: str,
        data: dict,
        **kwargs: dict,
    ) -> list[str]:
        """Serialize list of strings by stripping HTML."""
        values = super()._serialize(value, attr, data, **kwargs)
        if values:
            return [strip_html(value) for value in values]
        return []


def access_status(_: dict) -> dict:
    """Access status."""
    return {
        "id": "open",
        "icon": "unlock",
        "title_l10n": "Open",
        "description_l10n": "Open",
    }


def created_date_l10n_long(obj: dict) -> str:
    """Create date l10n long."""
    if "dates" in obj["metadata"] and len(obj["metadata"]["dates"]) > 0:
        return obj["metadata"]["dates"][0]
    return "N/A"


class OriginalSchema(Schema):
    """Original Schema."""

    view = fields.String(attribute="view")
    schema_l10n = fields.Method("get_schema_l10n")

    def get_schema_l10n(self, obj: dict) -> str:
        """Get schema l10n."""
        schemas = current_app.config.get("GLOBAL_SEARCH_ORIGINAL_SCHEMAS", {})
        for schema_name, schema in schemas.items():
            if schema_name == obj["schema"]:
                return schema["name_l10n"]
        return ""


class MetadataSchema(Schema):
    """Metadata."""

    subjects = StrippedHTMLList(attribute="subjects")
    publishers = StrippedHTMLList(attribute="publishers")
    contributors = StrippedHTMLList(attribute="contributors")
    dates = StrippedHTMLList(attribute="dates")
    types = StrippedHTMLList(attribute="types")
    formatts = StrippedHTMLList(attribute="formatts")
    identifiers = StrippedHTMLList(attribute="identifiers")
    sources = StrippedHTMLList(attribute="sources")
    languages = StrippedHTMLList(attribute="languages")
    releations = StrippedHTMLList(attribute="releations")
    coverages = StrippedHTMLList(attribute="coverages")
    rights = StrippedHTMLList(attribute="rights")
    creators = StrippedHTMLList(attribute="creators")
    titles = StrippedHTMLList(attribute="titles")
    descriptions = StrippedHTMLList(attribute="descriptions")


class GlobalSearchSchema(Schema):
    """Schema for dumping extra information for the global search record."""

    id = SanitizedUnicode(data_key="id", attribute="id")

    access_status = fields.Function(access_status)

    original = fields.Nested(OriginalSchema, attribute="original")

    created_date_l10n_long = fields.Function(created_date_l10n_long)

    metadata = fields.Nested(MetadataSchema, attribute="metadata")
