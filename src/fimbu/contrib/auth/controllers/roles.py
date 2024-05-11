"""Role Routes."""
from __future__ import annotations

from litestar import Controller
from litestar.di import Provide

from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.guards import requires_superuser
from fimbu.contrib.auth.service import UserService


class RoleController(Controller):
    """Handles the adding and removing of new Roles."""

    tags = ["Roles"]
    guards = [requires_superuser]
    dependencies = {
        "roles_service": Provide(provide_user_service),
    }
    signature_namespace = {"UserService": UserService}
