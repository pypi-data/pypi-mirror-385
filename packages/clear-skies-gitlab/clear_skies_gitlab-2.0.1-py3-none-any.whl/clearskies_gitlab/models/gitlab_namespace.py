from __future__ import annotations

from collections import OrderedDict
from typing import Any

from clearskies import Model
from clearskies.columns import Boolean, Datetime, Integer, Json, Select, String


class GitlabNamespace(Model):
    """Base model for namespaces."""

    id_column_name = "id"

    id = String()
    name = String()
    path = String()
    kind = Select(allowed_values=["group", "user"])
    full_path = String()
    avatar_url = String()
    web_url = String()
    billable_members_count = Integer()
    plan = Select(allowed_values=["free", "premium", "ultimate", "bronze", "silver", "gold"])
    end_date = Datetime()
    trial_ends_on = Datetime()
    trial = Boolean()
    root_repository_size = Integer()
    projects_count = Integer()
    max_seats_used = Integer()
    max_seats_used_changed_at = Datetime()
    seats_in_use = Integer()
    members_counts_with_descendants = Integer()
