from __future__ import annotations

from collections import OrderedDict
from typing import Any, Self

from clearskies.columns import Boolean, Datetime, Email, Integer, Json, String

from clearskies_gitlab.models import gitlab_rest_model


class GitlabRestCurrentUser(
    gitlab_rest_model.GitlabRestModel,
):
    """Model for current user."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "user"

    id = Integer()
    username = String()
    email = Email()
    name = String()
    state = String()
    locked = Boolean()
    avatar_url = String()
    web_url = String()
    created_at = Datetime()
    bio = String()
    public_email = Email()
    organization = String()
    bot = Boolean()
    last_sign_in_at = Datetime()
    confirmed_at = Datetime()
    last_activity_on = Datetime()
    identities = Json()
    can_create_group = Boolean()
    can_create_project = Boolean()
    two_factor_enabled = Boolean()
    external = Boolean()
    private_profile = Boolean()
    commit_email = Email()
