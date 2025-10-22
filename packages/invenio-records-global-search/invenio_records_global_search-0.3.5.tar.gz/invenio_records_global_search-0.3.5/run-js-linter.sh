#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-global-search is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

# Usage:
#   ./run-js-linter.sh [args]
# Arguments
# -i|--install: installs eslint-config-invenio

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

for arg in $@;
do
    case ${arg} in
	-i|--install)
	    npm install --no-save --no-package-lock @inveniosoftware/eslint-config-invenio@^2.0.0;;
	-f|--fix)
	    printf "${GREEN}Run eslint${NC}\n";
            npx eslint -c invenio_records_global_search/assets/semantic-ui/js/invenio_records_global_search/.eslintrc.yml invenio_records_global_search/**/*.js --fix;;
	*)
	    printf "Argument ${RED}$arg${NC} not supported\n"
	    exit;;
    esac
done

printf "${GREEN}Run eslint${NC}\n"

npx eslint \
    -c invenio_records_global_search/assets/semantic-ui/js/invenio_records_global_search/.eslintrc.yml \
    invenio_records_global_search/**/*.js
