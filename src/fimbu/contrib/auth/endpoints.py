from fimbu.contrib.auth.controllers import (
    AccessController,
    RoleController,
    UserRoleController,
    UserController
)

__handlers__ = [
    AccessController,
    RoleController,
    UserController,
    UserRoleController
]
