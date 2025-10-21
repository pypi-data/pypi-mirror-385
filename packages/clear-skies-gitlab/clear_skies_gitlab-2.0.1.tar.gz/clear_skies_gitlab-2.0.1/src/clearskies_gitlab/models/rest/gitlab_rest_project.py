from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import BelongsToId, BelongsToModel, Boolean, Datetime, HasMany, Integer, Json, Select, String

from clearskies_gitlab.backends.gitlab_rest_backend import GitlabRestBackend
from clearskies_gitlab.models import gitlab_project, gitlab_rest_model
from clearskies_gitlab.models.rest import (
    gitlab_rest_group_reference,
    gitlab_rest_namespace,
    gitlab_rest_project_variable_refence,
)


class GitlabRestProject(
    gitlab_rest_model.GitlabRestModel,
    gitlab_project.GitlabProject,
):
    """Model for projects."""

    backend = GitlabRestBackend(
        api_to_model_map={
            "namespace.id": ["namespace_id", "group_id"],
        }
    )

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects"

    group_id = BelongsToId(gitlab_rest_group_reference.GitlabRestGroupReference)
    group = BelongsToModel("group_id")

    namespace_id = BelongsToId(gitlab_rest_namespace.GitlabRestNamespace)
    namespace = BelongsToModel("namespace_id")

    variables = HasMany(
        gitlab_rest_project_variable_refence.GitlabRestProjectVariableReference,
        foreign_column_name="project_id",
    )
    ### Search params
    include_hidden = Boolean()
    include_pending_delete = Boolean()
    last_activity_after = Datetime()
    last_activity_before = Datetime()
    membership = Boolean()
    min_access_level = Integer()
    order_by = Select(
        allowed_values=[
            "id",
            "name",
            "path",
            "created_at",
            "updated_at",
            "star_count",
            "last_activity_at",
            "similarity",
        ]
    )
    owned = Boolean()
    repository_checksum_failed = Boolean()
    repository_storage = String()
    search_namespaces = Boolean()
    search = String()
    simple = Boolean()
    sort = String()
    starred = Boolean()
    topic_id = Integer()
    topic = String()
    updated_after = Datetime()
    updated_before = Datetime()
    visibility = Select(allowed_values=["public", "internal", "private"])
    wiki_checksum_failed = Boolean()
    with_custom_attributes = Boolean()
    with_issues_enabled = Boolean()
    with_merge_requests_enabled = Boolean()
    with_programming_language = String()
    marked_for_deletion_on = Datetime(date_format="%Y-%m-%d")
