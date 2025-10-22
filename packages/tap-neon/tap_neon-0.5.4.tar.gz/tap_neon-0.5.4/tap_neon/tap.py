"""Neon Serverless Postgres tap class."""

from __future__ import annotations

import sys

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_neon import streams

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


class TapNeon(Tap):
    """Singer tap for Neon Serverless Postgres."""

    name = "tap-neon"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="API Key for Neon Serverless Postgres",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Neon Serverless Postgres streams.
        """
        return [
            streams.Operations(tap=self),
            streams.Projects(tap=self),
            streams.Branches(tap=self),
            streams.Endpoints(tap=self),
            streams.Roles(tap=self),
            streams.Databases(tap=self),
            streams.Snapshots(tap=self),
        ]
