from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import Boolean, Integer, String

from clearskies_gitlab.models import gitlab_rest_model


class GitlabRestProjectRepositoryCommitDiff(
    gitlab_rest_model.GitlabRestModel,
):
    """Model for projects repository commits diff."""

    id_column_name = "commit_id"

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/repository/commits/:commit_id/diff"

    diff = String()
    new_path = String()
    old_path = String()
    a_mode = Integer()
    b_mode = Integer()
    new_file = Boolean()
    renamed_file = Boolean()
    deleted_file = Boolean()
    # search params
    project_id = Integer()
    commit_id = String()
    unidiff = Boolean()
