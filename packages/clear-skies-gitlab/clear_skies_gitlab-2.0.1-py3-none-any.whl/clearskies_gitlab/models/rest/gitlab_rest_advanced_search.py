from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import Boolean, Json, Select, String

from clearskies_gitlab.models import gitlab_rest_model


class GitlabRestAdvancedSearch(
    gitlab_rest_model.GitlabRestModel,
):
    """Model for groups access tokens."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "search"

    scope = Select(
        allowed_values=[
            "projects",
            "issues",
            "merge_requests",
            "milestones",
            "snippet_titles",
            "users",
            "wiki_blobs",
            "commits",
            "blobs",
            "notes",
        ]
    )
    search = String()
    confidential = Boolean()
    state = String()
    fields = Json()
