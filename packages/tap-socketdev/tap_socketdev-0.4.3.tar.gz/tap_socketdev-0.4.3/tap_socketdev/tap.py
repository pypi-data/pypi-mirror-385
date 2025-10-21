"""Socket tap class."""

from __future__ import annotations

import typing as t
from typing import override

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_socketdev import streams

if t.TYPE_CHECKING:
    from singer_sdk.streams import RESTStream


class TapSocketDev(Tap):
    """Singer tap for Socket.dev."""

    name = "tap-socketdev"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            title="API Key",
            description="API Key for Socket",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            title="Start Date",
            description="Earliest datetime to get data from",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[RESTStream]:
        return [
            streams.Reports(tap=self),
            streams.Organizations(tap=self),
            streams.Repositories(tap=self),
            streams.RepoLabels(tap=self),
        ]
