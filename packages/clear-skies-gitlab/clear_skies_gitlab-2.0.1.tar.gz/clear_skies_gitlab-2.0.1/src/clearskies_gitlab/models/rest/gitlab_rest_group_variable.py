from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Self

from clearskies.columns import BelongsToId, BelongsToModel, String

from clearskies_gitlab.models import gitlab_cicd_variable, gitlab_rest_model


class GitlabRestGroupVariable(
    gitlab_rest_model.GitlabRestModel,
    gitlab_cicd_variable.GitlabCICDVariable,
):
    """Model for gitlab group variables."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/variables"

    group_id = String()
