// This file is part of Invenio.
//
// Copyright (C) 2023-2024 Graz University of Technology.
//
// invenio-records-global-search is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE file for
// more details.

import { parametrize } from "react-overridable";
import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  RDMRecordSearchBarContainer,
  RDMRecordMultipleSearchBarElement,
  RDMToggleComponent,
  RDMCountComponent,
  RDMErrorComponent,
  RDMEmptyResults,
} from "@js/invenio_app_rdm/search/components";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";
import {
  // GlobalSearchRecordResultsGridItem,
  GlobalSearchRecordResultsListItem,
  GlobalSearchEmptyResults,
  GlobalSearchBucketAggregationElement,
} from "./components";

const appName = "GlobalSearchRecords.Search";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toggle: false,
});

const RDMRecordSearchBarContainerWithConfig = parametrize(
  RDMRecordSearchBarContainer,
  {
    appName: appName,
  }
);

const initSearchApp = createSearchAppInit({
  "BucketAggregation.element": GlobalSearchBucketAggregationElement,
  "BucketAggregationValues.element": ContribBucketAggregationValuesElement,
  "EmptyResults.element": GlobalSearchEmptyResults,
  // "ResultsGrid.item": GlobalSearchRecordResultsGridItem,
  "ResultsList.item": GlobalSearchRecordResultsListItem,
  "SearchApp.facets": ContribSearchAppFacetsWithConfig,
  "SearchApp.searchbarContainer": RDMRecordSearchBarContainerWithConfig,
  "SearchBar.element": RDMRecordMultipleSearchBarElement,
  "SearchFilters.ToggleComponent": RDMToggleComponent,
  // "Error.element": RDMErrorComponent,
  "Count.element": RDMCountComponent,
});
