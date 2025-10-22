// This file is part of Invenio.
//
// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-global-search is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE file for
// more details.

import React, { useState } from "react";
import { Card, Icon } from "semantic-ui-react";

export const GlobalSearchBucketAggregationElement = ({
  title,
  containerCmp,
}) => {
  const [active, setActive] = useState(true);

  return (
    <Card className="borderless facet">
      <Card.Content>
        <Card.Header
          as="h2"
          style={{ float: "left", minHeight: 0, cursor: "pointer" }}
          onClick={() => setActive((active) => !active)}
        >
          <Icon
            style={{ "margin-top": "-4px" }}
            name={active ? "angle down" : "angle right"}
          />
          {title}
        </Card.Header>
        {active ? containerCmp : null}
      </Card.Content>
    </Card>
  );
};
