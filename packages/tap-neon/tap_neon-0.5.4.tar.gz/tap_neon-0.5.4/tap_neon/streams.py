"""Stream type classes for tap-neon."""

from __future__ import annotations

import sys
import typing as t
from copy import deepcopy
from importlib import resources

from singer_sdk import OpenAPISchema, StreamSchema

from tap_neon import openapi
from tap_neon.client import NeonStream

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context, Record


__all__ = [
    "Branches",
    "Databases",
    "Endpoints",
    "Operations",
    "Projects",
    "Roles",
    "Snapshots",
]


def not_required_null(schema: dict[str, t.Any]) -> dict[str, t.Any]:
    """Add 'null' to the type of all properties that are not required."""
    new_schema = deepcopy(schema)
    schema_type: str | list[str] = new_schema.get("type")  # type: ignore[assignment]
    if "object" not in schema_type:
        errmsg = "Schema type must be of 'object' type"
        raise ValueError(errmsg)

    required = new_schema.get("required", [])

    for prop in new_schema.get("properties", {}).values():
        prop_type: str | list[str] = prop.pop("type", [])
        if prop not in required and "null" not in prop_type:
            prop["type"] = (
                [prop_type, "null"]
                if isinstance(prop_type, str)
                else [*prop_type, "null"]
            )

        if "object" in prop_type:
            prop.update(not_required_null(prop))

    return new_schema


class NeonOpenAPI(OpenAPISchema):
    @override
    def fetch_schema(self, key: str) -> dict[str, t.Any]:
        schema = not_required_null(super().fetch_schema(key))
        if key == "ProjectListItem":
            schema["properties"]["default_endpoint_settings"]["properties"][
                "autoscaling_limit_min_cu"
            ]["minimum"] = 0
            schema["properties"]["default_endpoint_settings"]["properties"][
                "autoscaling_limit_max_cu"
            ]["minimum"] = 0
        elif key == "Endpoint":
            schema["properties"]["pooler_mode"]["enum"].append("READ_ONLY")
        return schema


OPENAPI_SCHEMA = NeonOpenAPI(resources.files(openapi) / "openapi.json")


class Projects(NeonStream):
    """Projects stream."""

    name = "projects"
    path = "/projects"
    primary_keys = ("id",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="ProjectListItem")
    records_jsonpath = "$.projects[*]"

    @override
    def get_child_context(
        self,
        record: Record,
        context: Context | None,
    ) -> dict[str, t.Any]:
        """Return the child context for this record.

        Args:
            record: The record to get the child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"project_id": record["id"]}


class Operations(NeonStream):
    """Operations stream."""

    name = "operations"
    path = "/projects/{project_id}/operations"
    primary_keys = ("id",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="Operation")
    records_jsonpath = "$.operations[*]"
    next_page_token_jsonpath = "$.pagination.cursor"  # noqa: S105
    parent_stream_type = Projects


class Branches(NeonStream):
    """Branches stream."""

    name = "branches"
    path = "/projects/{project_id}/branches"
    primary_keys = ("id",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="Branch")
    records_jsonpath = "$.branches[*]"
    parent_stream_type = Projects

    @override
    def get_child_context(
        self,
        record: Record,
        context: Context | None,
    ) -> dict[str, t.Any]:
        """Add branch_id to context.

        Args:
            record: A record dict.
            context: A context dict.

        Returns:
            The updated context dict.
        """
        return {
            "project_id": record["project_id"],
            "branch_id": record["id"],
        }


class Databases(NeonStream):
    """Databases stream."""

    name = "databases"
    path = "/projects/{project_id}/branches/{branch_id}/databases"
    primary_keys = ("id",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="Database")
    records_jsonpath = "$.databases[*]"
    parent_stream_type = Branches


class Roles(NeonStream):
    """Roles stream."""

    name = "roles"
    path = "/projects/{project_id}/branches/{branch_id}/roles"
    primary_keys = ("name",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="Role")
    records_jsonpath = "$.roles[*]"
    parent_stream_type = Branches


class Endpoints(NeonStream):
    """Endpoints stream."""

    name = "endpoints"
    path = "/projects/{project_id}/endpoints"
    primary_keys = ("id",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="Endpoint")
    records_jsonpath = "$.endpoints[*]"
    parent_stream_type = Projects


class Snapshots(NeonStream):
    """Snapshots stream."""

    name = "snapshots"
    path = "/projects/{project_id}/snapshots"
    primary_keys = ("id",)
    replication_key = None
    schema = StreamSchema(OPENAPI_SCHEMA, key="Snapshot")
    records_jsonpath = "$.snapshots[*]"
    parent_stream_type = Projects
