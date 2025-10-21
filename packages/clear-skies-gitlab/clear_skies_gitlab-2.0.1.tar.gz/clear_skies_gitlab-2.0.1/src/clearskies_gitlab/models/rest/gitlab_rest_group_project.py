from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import (
    BelongsToId,
    BelongsToModel,
    BelongsToSelf,
    Boolean,
    Datetime,
    HasMany,
    Integer,
    Json,
    Select,
    String,
)

from clearskies_gitlab.models import gitlab_project, gitlab_rest_model
from clearskies_gitlab.models.rest import (
    gitlab_rest_group_access_token,
    gitlab_rest_group_subgroup_reference,
    gitlab_rest_group_variable,
    gitlab_rest_project_reference,
)


class GitlabRestGroupProject(
    gitlab_rest_model.GitlabRestModel,
    gitlab_project.GitlabProject,
):
    """Model for groups projects."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/projects"
