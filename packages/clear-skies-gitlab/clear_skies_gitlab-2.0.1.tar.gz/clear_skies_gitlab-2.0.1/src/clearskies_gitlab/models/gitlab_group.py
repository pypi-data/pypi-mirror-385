from __future__ import annotations

from collections import OrderedDict
from typing import Any

from clearskies import Model
from clearskies.columns import Boolean, Datetime, Integer, Json, String


class GitlabGroup(Model):
    """Base model for groups."""

    id_column_name = "id"

    id = String()
    web_url = String()
    name = String()
    path = String()
    description = String()
    visibility = String()
    share_with_group_lock = Boolean()
    require_two_factor_authentication = Boolean()
    two_factor_grace_period = Integer()
    project_creation_level = String()
    auto_devops_enabled = Boolean()
    subgroup_creation_level = String()
    emails_disabled = Boolean()
    emails_enabled = Boolean()
    mentions_disabled = String()
    lfs_enabled = String()
    math_rendering_limits_enabled = Boolean()
    lock_math_rendering_limits_enabled = Boolean()
    default_branch = String()
    default_branch_protection = String()
    default_branch_protection_defaults = String()
    avatar_url = String()
    request_access_enabled = Boolean()
    full_name = String()
    full_path = String()
    created_at = Datetime()
    parent_id = String()
    organization_id = String()
    shared_runners_setting = String()
    custom_attributes = Json()
    statistics = Json()
    ldap_cn = String()
    ldap_access = String()
    ldap_group_links = Json()
    saml_group_links = Json()
    file_template_project_id = String()
    marked_for_deletion_on = Datetime()
    wiki_access_level = String()
    repository_storage = String()
    duo_features_enabled = Boolean()
    lock_duo_features_enabled = Boolean()
    shared_with_groups = Json()
    runners_token = String()
    enabled_git_access_protocol = String()
    prevent_sharing_groups_outside_hierarchy = Boolean()
    shared_runners_minutes_limit = Integer()
    extra_shared_runners_minutes_limit = Integer()
    prevent_forking_outside_group = Boolean()
    service_access_tokens_expiration_enforced = Boolean()
    membership_lock = Boolean()
    ip_restriction_ranges = Json()
    unique_project_download_limit = String()
    unique_project_download_limit_interval_in_seconds = Integer()
    unique_project_download_limit_alertlist = Json()
    auto_ban_user_on_excessive_projects_download = Boolean()
