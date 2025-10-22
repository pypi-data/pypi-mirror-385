# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""JS/CSS Webpack bundles for theme."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "invenio-records-global-search-theme": "./less/invenio_records_global_search/theme.less",
                "invenio-records-global-search-search": "./js/invenio_records_global_search/search/index.js",
            },
            "dependencies": {},
            "aliases": {
                "@js/invenio_records_global_search": "js/invenio_records_global_search",
                "@less/invenio_records_global_search": "less/invenio_records_global_search",
                "@translations/invenio_records_global_search": "translations/invenio_records_global_search",
            },
        },
    },
)
