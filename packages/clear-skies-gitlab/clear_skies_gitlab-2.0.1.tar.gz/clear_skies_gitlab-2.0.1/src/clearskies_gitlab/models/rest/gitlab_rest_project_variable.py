from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import BelongsToId, BelongsToModel

from clearskies_gitlab.models import gitlab_cicd_variable, gitlab_rest_model
from clearskies_gitlab.models.rest import gitlab_rest_project_reference


class GitlabRestProjectVariable(
    gitlab_rest_model.GitlabRestModel,
    gitlab_cicd_variable.GitlabCICDVariable,
):
    """Model for gitlab group variables."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/variables"

    project_id = BelongsToId(gitlab_rest_project_reference.GitlabRestProjectReference)
    project = BelongsToModel("project_id")
