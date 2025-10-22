# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Global Search Services."""
from typing import Any

from flask import current_app
from flask_principal import Identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.records.results import RecordItem, RecordList
from invenio_records_resources.services.uow import UnitOfWork, unit_of_work

from .utils import (
    build_gs_id_query,
    remove_parent_id_q,
    replace_query_params_with_known_schema,
)


class GlobalSearchRecordService(RecordService):
    """Global search record service."""

    @unit_of_work()
    def create_or_update(
        self,
        identity: Identity,
        data: dict,
        uow: UnitOfWork | None = None,
        *,
        expand: bool = False,
    ) -> RecordItem:
        """Create a record.

        :param identity: Identity of user creating the record.
        :param data: Input data according to the data schema.
        """
        gs_pid = "gs-" + data["original"]["pid"]

        try:
            # only to check if a exists already
            self.record_cls.pid.resolve(gs_pid)

            return self.update(identity, id_=gs_pid, data=data)
        except PIDDoesNotExistError:
            self.record_cls.gs_pid = gs_pid
            return self._create(self.record_cls, identity, data, uow=uow, expand=expand)

    def search(
        self,
        identity: Identity,
        params: dict | None = None,
        search_preference: str | None = None,
        expand: bool = False,  # noqa: FBT001, FBT002
        **kwargs: Any,  # noqa: ANN401
    ) -> RecordList:
        """Search for records matching the querystring.

        Method was overriden to rework query params that come as default from invenio-app-rdm
        into the global-search schema structure.
        """
        try:
            schema = self.config.schema
            metadata_field = schema().fields.get("metadata")
            metadata_schema = metadata_field.nested
        except AttributeError:
            current_app.logger("WARN: Schema unknown for query pre-processing")
            return super().search(
                identity,
                params=params,
                search_preference=search_preference,
                expand=expand,
                **kwargs,
            )

        if "q" not in params:
            return super().search(
                identity,
                params=params,
                search_preference=search_preference,
                expand=expand,
                **kwargs,
            )

        query = params["q"]
        if "parent.id" in query:
            # For queries that depend on the original parent record:
            # search for the original record because there is no connection
            # between original-parent.id and gs.record.
            # For now the workaround is implemented only for RDM-Records.
            original_records = current_rdm_records_service.search(
                identity,
                params=params,
                search_preference=search_preference,
                expand=expand,
                **kwargs,
            )

            # the query above returns only the final rdm-record version
            last_version = next(original_records.hits)

            # search for all versions based on the last published version
            original_all_versions = current_rdm_records_service.search_versions(
                identity,
                last_version.get("id") or "",
                params=params,
                search_preference=search_preference,
                expand=expand,
                **kwargs,
            )

            # edit gs query
            query_wo_pid = remove_parent_id_q(query)
            params["q"] = build_gs_id_query(original_all_versions) + query_wo_pid

        for metadata_field_name in metadata_schema().fields:
            if metadata_field_name in params["q"]:
                full_q = params["q"]
                params["q"] = replace_query_params_with_known_schema(
                    full_q,
                    metadata_field_name,
                )

        return super().search(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            **kwargs,
        )
