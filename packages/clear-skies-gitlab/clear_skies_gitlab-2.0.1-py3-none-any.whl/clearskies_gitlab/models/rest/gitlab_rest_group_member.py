from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import BelongsToId, BelongsToModel, Boolean, Json, String

from clearskies_gitlab.models import gitlab_member, gitlab_rest_model
from clearskies_gitlab.models.rest import gitlab_rest_group


class GitlabRestGroupMember(
    gitlab_rest_model.GitlabRestModel,
    gitlab_member.GitlabMember,
):
    """Model for group members."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/members"

    group_id = String()
    query = String()
    user_ids = Json()
    skip_users = Json()
    show_seat_info = Boolean()
    all = Boolean()
