from fimbu.contrib.auth.controllers import (
    AccessController, PasswordController,
    UserManagementController, RoleManagementController
)


__handlers__ = [
    AccessController,
    PasswordController,
    UserManagementController,
    RoleManagementController
]
