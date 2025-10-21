from __future__ import annotations

from clearskies import Model

from clearskies_gitlab.backends import GitlabRestBackend


class GitlabRestModel(Model):
    """Base model for rest api."""

    backend = GitlabRestBackend()
