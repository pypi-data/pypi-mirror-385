from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import Boolean, Datetime, Email, Integer, Json, String

from clearskies_gitlab.models import gitlab_rest_model


class GitlabRestProjectRepositoryCommit(
    gitlab_rest_model.GitlabRestModel,
):
    """Model for projects repository commits."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/repository/commits"

    id = String()
    short_id = String()
    title = String()
    author_name = String()
    author_email = Email()
    authored_date = Datetime()
    committer_name = String()
    committer_email = Email()
    committed_date = Datetime()
    created_at = Datetime()
    messsage = String()
    parent_ids = Json()
    web_url = String()
    extended_trailers = Json()
    # search params
    project_id = Integer()
    ref_name = String()
    since = Datetime()
    until = Datetime()
    path = String()
    all = Boolean()
    with_stats = Boolean()
    first_parent = Boolean()
    trailers = Boolean()
