// This file is part of Invenio.
//
// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-global-search is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE file for
// more details.

import React, { useState } from "react";
import { Card, Grid, Header, Button, Segment, Icon } from "semantic-ui-react";
import { Trans } from "react-i18next";
import { i18next } from "../../../../translations/invenio_records_global_search/i18next";

export const GlobalSearchEmptyResults = ({
  queryString,
  searchPath,
  resetQuery,
}) => {
  return (
    <Grid>
      <Grid.Row centered>
        <Grid.Column width={12} textAlign="center">
          <Header as="h2">
            {i18next.t("We couldn't find any matches for {{- search}}", {
              search: (queryString && `'${queryString}'`) || "your search",
            })}
          </Header>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row centered>
        <Grid.Column width={8} textAlign="center">
          <Button primary onClick={resetQuery}>
            <Icon name="search" />
            {i18next.t("Start over")}
          </Button>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row centered>
        <Grid.Column width={12}>
          <Segment secondary padded size="large">
            <Header as="h3" size="small">
              {i18next.t("ProTip")}!
            </Header>
            <Trans>
              <p>
                For more tips, check out our{" "}
                <a href="/help/search" title={i18next.t("Search guide")}>
                  search guide
                </a>{" "}
                for defining advanced search queries.
              </p>
            </Trans>
          </Segment>
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};
