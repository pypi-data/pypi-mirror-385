# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Original system field."""

from invenio_records.systemfields.base import SystemField
from invenio_records_resources.records.api import Record


class OriginalField(SystemField):
    """OriginalField."""

    def __init__(
        self,
        key: str = "original",
        *,
        clear_none: bool = False,
        create_if_missing: bool = True,
    ) -> None:
        """Initialise the dict field.

        :param key: Key to set (dot notation supported).
        :param clear_none: Boolean to control if empty/None values should be
                           removed.
        :param create_if_missing: If a subkey is missing it will be created if
                                  this option is set to true.
        """
        self.clear_none = clear_none
        self.create_if_missing = create_if_missing
        super().__init__(key=key)

    def __set__(self, record: Record, value: dict | list | str) -> None:
        """Set."""
        self.set_dictkey(record, value, create_if_missing=self.create_if_missing)
