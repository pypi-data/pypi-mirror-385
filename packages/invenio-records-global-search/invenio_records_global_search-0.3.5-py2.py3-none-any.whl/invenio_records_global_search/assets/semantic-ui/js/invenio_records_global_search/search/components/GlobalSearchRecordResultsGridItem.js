// This file is part of Invenio.
//
// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-global-search is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE file for
// more details.

import React from "react";
import { get, truncate } from "lodash";
import { Card } from "semantic-ui-react";

export const GlobalSearchRecordResultsGridItem = ({ result, index }) => {
  const metadata = get(result, ["ui", "metadata", "json"], []);
  const description = get(
    metadata,
    ["summary", "0", "summary"],
    "No description"
  );
  return (
    <Card fluid key={index} href={`/global-search/${result.pid}`}>
      <Card.Content>
        <Card.Header>{result.metadata.json.title_statement.title}</Card.Header>
        <Card.Description>
          {truncate(description, { length: 200 })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
};
