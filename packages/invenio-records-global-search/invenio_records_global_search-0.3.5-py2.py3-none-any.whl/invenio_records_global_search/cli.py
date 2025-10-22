# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CLI."""

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity

from .proxies import current_records_global_search


@click.group()
def global_search() -> None:
    """CLI-group for "invenio record global search" commands."""


@global_search.command()
@with_appcontext
def rebuild_index() -> None:
    """Reindex all records."""
    click.secho("Reindexing records of global search...", fg="green")

    service = current_records_global_search.records_service  # type: ignore[attr-defined]
    service.rebuild_index(identity=system_identity)

    click.secho("Reindexed records!", fg="green")


@global_search.command()
@with_appcontext
def rebuild_database() -> None:
    """Rebuild database."""
    for func in current_app.config.get("GLOBAL_SEARCH_REBUILD_DATABASE", []):
        func()
