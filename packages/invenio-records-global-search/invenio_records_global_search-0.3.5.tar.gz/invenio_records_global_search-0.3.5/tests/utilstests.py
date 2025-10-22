# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utils tests."""

import pytest

from invenio_records_global_search.services.utils import (
    replace_query_params_with_known_schema,
)


@pytest.mark.parametrize(
    ("full_q", "known_field", "expected"),
    [
        (
            "metadata.creators.person_or_org.name: TestFirstName, TestLastName",
            "creators",
            "metadata.creators: TestFirstName, TestLastName",
        ),
        (
            "metadata.rights.details: test_details and metadata.rights.test_field: test_value",
            "rights",
            "metadata.rights: test_details and metadata.rights: test_value",
        ),
        (
            "+metadata.title.details: test_details -metadata.title.test_field1: test_value",
            "title",
            "+metadata.title: test_details -metadata.title: test_value",
        ),
    ],
)
def test_diff_element_description_match_key(  # noqa: D103
    full_q: str,
    known_field: str,
    expected: str,
) -> None:
    assert (  # noqa: S101
        replace_query_params_with_known_schema(full_q, known_field) == expected
    )
