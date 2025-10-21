"""Stream type classes for tap-socketdev."""

from __future__ import annotations

import typing as t
from typing import override

from singer_sdk import typing as th
from singer_sdk.pagination import BasePageNumberPaginator

from tap_socketdev.client import SocketDevStream

if t.TYPE_CHECKING:
    from requests import Response
    from singer_sdk.helpers.types import Context


class Reports(SocketDevStream):
    """Reports stream."""

    name = "reports"
    path = "/v0/report/list"
    records_jsonpath = "$[*]"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The report's unique identifier",
        ),
        th.Property(
            "url",
            th.StringType,
            description="The URL to the report",
        ),
    ).to_dict()


class Organizations(SocketDevStream):
    """Organizations stream."""

    name = "organizations"
    path = "/v0/organizations"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The organization's unique identifier",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The organization's name",
        ),
        th.Property(
            "image",
            th.StringType,
            description="The organization's image",
        ),
        th.Property(
            "plan",
            th.StringType,
            description="The organization's plan",
        ),
    ).to_dict()

    @override
    def parse_response(self, response: Response) -> t.Generator[dict, None, None]:
        yield from response.json()["organizations"].values()

    @override
    def generate_child_contexts(
        self,
        record: dict[str, t.Any],
        context: Context | None,
    ) -> t.Iterable[Context | None]:
        yield {
            "org_slug": record["slug"],
        }


class Repositories(SocketDevStream):
    """Repositories stream."""

    name = "repositories"
    path = "/v0/orgs/{org_slug}/repos"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.nextPage"  # noqa: S105
    primary_keys = ("id",)
    replication_key = None

    parent_stream_type = Organizations

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The repository's unique identifier",
        ),
        th.Property(
            "created_at",
            th.DateTimeType,
            description="The creation date of the repository",
        ),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="The last update date of the repository",
        ),
        th.Property(
            "slug",
            th.StringType,
            description="The slug of the repository",
        ),
        th.Property(
            "head_full_scan_id",
            th.StringType,
            description="The ID of the head full scan of the repository",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The name of the repository",
        ),
        th.Property(
            "description",
            th.StringType,
            description="The description of the repository",
        ),
        th.Property(
            "homepage",
            th.StringType,
            description="The homepage URL of the repository",
        ),
        th.Property(
            "visibility",
            th.StringType,
            description="The visibility of the repository",
            allowed_values=["public", "private"],
        ),
        th.Property(
            "archived",
            th.BooleanType,
            description="Whether the repository is archived or not",
        ),
        th.Property(
            "default_branch",
            th.StringType,
            description="The default branch of the repository",
        ),
        th.Property(
            "org_slug",
            th.StringType,
            description="The slug of the organization the repository belongs to",
        ),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict[str, t.Any] | str:
        return {
            "page": next_page_token,
            "per_page": 100,
            "sort": "updated_at",
            "direction": "asc",
        }


class RepoLabels(SocketDevStream):
    """Repo labels stream."""

    name = "repo_labels"
    path = "/v0/orgs/{org_slug}/repos/labels"
    records_jsonpath = "$.results[*]"
    primary_keys = ("id",)
    replication_key = None

    parent_stream_type = Organizations

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The ID of the label",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The name of the label",
        ),
        th.Property(
            "repository_ids",
            th.ArrayType(th.StringType),
            description="The IDs of repositories this label is associated with",
        ),
        th.Property(
            "has_security_policy",
            th.BooleanType,
            description="Whether the label has a security policy",
            default=False,
        ),
        th.Property(
            "has_license_policy",
            th.BooleanType,
            description="Whether the label has a license policy",
            default=False,
        ),
        th.Property(
            "org_slug",
            th.StringType,
            description="The slug of the organization the label belongs to",
        ),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict[str, t.Any] | str:
        return {
            "page": next_page_token,
            "per_page": 100,
        }

    @override
    def get_new_paginator(self) -> BasePageNumberPaginator | None:
        return BasePageNumberPaginator(start_value=1)
