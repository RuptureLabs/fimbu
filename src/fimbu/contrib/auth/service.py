from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, Sequence, TypeVar
from uuid import UUID

from jose import JWTError
from litestar.contrib.jwt.jwt_token import Token
from fimbu.contrib.auth.models import PermissionScope, Permission
from fimbu.contrib.auth.protocols import PermScopteT, PermT, UserT
from fimbu.contrib.auth.exceptions import InvalidTokenException
from fimbu.contrib.auth.schemas import PermissionUpdate
from fimbu.utils.crypto import PasswordManager
from fimbu.db import ResultConverter

from fimbu.contrib.auth.repository import (
    PermissionRepository,
    PermissionScopeRepository,
    UserRepository
)

from fimbu.db.exceptions import DuplicateRecordError, ObjectNotFound

__all__ = ["BaseUserService", "UserService"]


if TYPE_CHECKING:
    from litestar import Request
    from fimbu.contrib.auth.schemas import AccountLogin


class BaseUserService(Generic[UserT], ResultConverter):  # pylint: disable=R0904
    """Main user management interface."""

    user_model: type[UserT]
    """A subclass of the `User` ORM model."""

    def __init__(
        self,
        user_repository: UserRepository[UserT],
        secret: str,
        hash_schemes: Sequence[str] | None = None,
    ) -> None:
        """User service constructor.

        Args:
            user_repository: A `UserRepository` instance.
            secret: Secret string for securely signing tokens.
            hash_schemes: Schemes to use for password encryption.
            role_repository: A `RoleRepository` instance.
        """
        self.user_repository = user_repository
        self.permission_scope_repository = PermissionScopeRepository()
        self.permission_repository = PermissionRepository()
        self.secret = secret
        self.password_manager = PasswordManager(hash_schemes=hash_schemes)
        self.user_model = self.user_repository.model_type
        

    async def add_user(self, user: UserT, verify: bool = False, activate: bool = True) -> UserT:
        """Create a new user programmatically.

        Args:
            user: User model instance.
            verify: Set the user's verification status to this value.
            activate: Set the user's active status to this value.
        """
        existing_user = await self.user_repository.exists(email=user.email)
        if existing_user:
            raise DuplicateRecordError("email already associated with an account")

        user.is_verified = verify
        user.is_active = activate

        user = await self.user_repository.add(user)
        scopes = await self.perm_scope_repository.list(default=True)
        permissions = [s.create_permission(user) for s in scopes]
        
        await self.permission_repository.add_many(permissions)

        return user


    async def register(self, data: dict[str, Any], request: Request | None = None) -> UserT:
        """Register a new user and optionally run custom business logic.

        Args:
            data: User creation data transfer object.
            request: The litestar request that initiated the action.
        """
        await self.pre_registration_hook(data, request)

        data["password_hash"] = await self.password_manager.get_password_hash(data.pop("password"))
        user = await self.add_user(self.user_model(**data))  # type: ignore[arg-type]
        await self.initiate_verification(user)  # TODO: make verification optional?

        await self.post_registration_hook(user, request)

        return user

    async def get_user(self, id_: "UUID") -> UserT:
        """Retrieve a user from the database by id.

        Args:
            id_: UUID corresponding to a user primary key.
        """
        return await self.user_repository.get(id_)
    
    
    async def get_all_users(self) -> list[UserT]:
        """Retrieve all users from the database."""
        return await self.user_repository.list()

    async def get_user_by(self, **kwargs: Any) -> UserT | None:
        """Retrieve a user from the database by arbitrary keyword arguments.

        Args:
            **kwargs: Keyword arguments to pass as filters.

        Examples:
            ```python
            service = UserService(...)
            john = await service.get_one(email="john@example.com")
            ```
        """
        return await self.user_repository.get_one_or_none(**kwargs)

    async def update_user(self, data: UserT) -> UserT:
        """Update arbitrary user attributes in the database.

        Args:
            data: User update data transfer object.
        """

        return await self.user_repository.update(data)

    async def delete_user(self, id_: "UUID") -> UserT:
        """Delete a user from the database.

        Args:
            id_: UUID corresponding to a user primary key.
        """
        return await self.user_repository.delete(id_)

    async def authenticate(self, data: AccountLogin, request: Request | None = None) -> UserT | None:
        """Authenticate a user.

        Args:
            data: User authentication data transfer object.
            request: The litestar request that initiated the action.
        """
        # avoid early returns to mitigate timing attacks.
        # check if user supplied logic should allow authentication, but only
        # supply the result later.
        should_proceed = await self.pre_login_hook(data, request)

        try:
            user = await self.user_repository.get_one(email=data.email)
        except ObjectNotFound:
            # trigger passlib's `dummy_verify` method
            self.password_manager.verify_and_update(data.password, None)
            return None

        password_verified, new_password_hash = self.password_manager.verify_and_update(
            data.password, user.password_hash
        )
        if new_password_hash is not None:
            user = await self.user_repository.update_instance(user, {"password_hash": new_password_hash})

        if not password_verified or not should_proceed:
            return None

        await self.post_login_hook(user, request)

        return user

    def generate_token(self, user_id: "UUID", aud: str) -> str:
        """Generate a limited time valid JWT.

        Args:
            user_id: UUID of the user to provide the token to.
            aud: Context of the token
        """
        token = Token(
            exp=datetime.now() + timedelta(seconds=60 * 60 * 24),  # noqa: DTZ005
            sub=str(user_id),
            aud=aud,
        )
        return token.encode(secret=self.secret, algorithm="HS256")

    async def initiate_verification(self, user: UserT) -> None:
        """Initiate the user verification flow.

        Args:
            user: The user requesting verification.
        """
        token = self.generate_token(user.id, aud="verify")
        await self.send_verification_token(user, token)

    async def send_verification_token(self, user: UserT, token: str) -> None:
        """Execute custom logic to send the verification token to the relevant user.

        Args:
            user: The user requesting verification.
            token: An encoded JWT bound to verification.

        Notes:
        - Develepors need to override this method to facilitate sending the token via email, sms etc.
        """

    async def verify(self, encoded_token: str, request: Request | None = None) -> UserT:
        """Verify a user with the given JWT.

        Args:
            encoded_token: An encoded JWT bound to verification.
            request: The litestar request that initiated the action.

        Raises:
            InvalidTokenException: If the token is expired or tampered with.
        """
        token = self._decode_and_verify_token(encoded_token, context="verify")

        user_id = token.sub
        try:
            user = await self.user_repository.update(self.user_model(id=UUID(user_id), is_verified=True))  # type: ignore[arg-type]
        except ObjectNotFound as e:
            raise InvalidTokenException("token is invalid") from e

        await self.post_verification_hook(user, request)

        return user

    async def initiate_password_reset(self, email: str) -> None:
        """Initiate the password reset flow.

        Args:
            email: Email of the user who has forgotten their password.
        """
        user = await self.get_user_by(email=email)  # TODO: something about timing attacks.
        if user is None:
            return
        token = self.generate_token(user.id, aud="reset_password")
        await self.send_password_reset_token(user, token)

    async def send_password_reset_token(self, user: UserT, token: str) -> None:
        """Execute custom logic to send the password reset token to the relevant user.

        Args:
            user: The user requesting the password reset.
            token: An encoded JWT bound to the password reset flow.

        Notes:
        - Develepors need to override this method to facilitate sending the token via email, sms etc.
        """

    async def reset_password(self, encoded_token: str, password: str) -> None:
        """Reset a user's password given a valid JWT.

        Args:
            encoded_token: An encoded JWT bound to the password reset flow.
            password: The new password to hash and store.

        Raises:
            InvalidTokenException: If the token has expired or been tampered with.
        """
        token = self._decode_and_verify_token(encoded_token, context="reset_password")

        user_id = token.sub
        try:
            await self.user_repository.update(
                self.user_model(id=UUID(user_id), password_hash=self.password_manager.hash(password))  # type: ignore[arg-type]
            )
        except ObjectNotFound as e:
            raise InvalidTokenException from e

    async def pre_login_hook(
        self, data: AccountLogin, request: Request | None = None
    ) -> bool:  # pylint: disable=W0613
        """Execute custom logic to run custom business logic prior to authenticating a user.

        Useful for authentication checks against external sources,
        eg. current membership validity or blacklists, etc
        Must return `False` or raise a custom exception to cancel authentication.

        Args:
            data: Authentication data transfer object.
            request: The litestar request that initiated the action.

        Notes:
            Uncaught exceptions in this method will break the authentication process.
        """
        return True

    async def post_login_hook(self, user: UserT, request: Request | None = None) -> None:
        """Execute custom logic to run custom business logic after authenticating a user.

        Useful for eg. updating a login counter, updating last known user IP
        address, etc.

        Args:
            user: The user who has authenticated.
            request: The litestar request that initiated the action.

        Notes:
            Uncaught exceptions in this method will break the authentication process.
        """
        return

    async def pre_registration_hook(
        self, data: dict[str, Any], request: Request | None = None
    ) -> None:  # pylint: disable=W0613
        """Execute custom logic to run custom business logic prior to registering a user.

        Useful for authorization checks against external sources,
        eg. membership API or blacklists, etc.

        Args:
            data: User creation data transfer object
            request: The litestar request that initiated the action.

        Notes:
        - Uncaught exceptions in this method will result in failed registration attempts.
        """
        return

    async def post_registration_hook(self, user: UserT, request: Request | None = None) -> None:
        """Execute custom logic to run custom business logic after registering a user.

        Useful for updating external datasets, sending welcome messages etc.

        Args:
            user: User ORM instance.
            request: The litestar request that initiated the action.

        Notes:
        - Uncaught exceptions in this method could result in returning a HTTP 500 status
        code while successfully creating the user in the database.
        - It's possible to skip verification entirely by setting `user.is_verified`
        to `True` here.
        """
        return

    async def post_verification_hook(self, user: UserT, request: Request | None = None) -> None:
        """Execute custom logic to run custom business logic after a user has verified details.

        Useful for eg. updating sales lead data, etc.

        Args:
            user: User ORM instance.
            request: The litestar request that initiated the action.

        Notes:
        - Uncaught exceptions in this method could result in returning a HTTP 500 status
        code while successfully validating the user.
        """
        return

    def _decode_and_verify_token(self, encoded_token: str, context: str) -> Token:
        try:
            token = Token.decode(
                encoded_token=encoded_token,
                secret=self.secret,
                algorithm="HS256",
            )
        except JWTError as e:
            raise InvalidTokenException from e

        if token.aud != context:
            raise InvalidTokenException(f"aud value must be {context}")

        return token
    

    async def get_all_scopes(self) -> list[PermissionScope]:
        """
        Get all scopes.

        Returns:
            list[PermissionScope]: A list of all scopes.
        """
        return await self.permission_scope_repository.list()


    async def get_scope_permissions(self, scope: PermScopteT ) -> list[Permission]:
        """
        Get all permissions for a given scope.
        
        Args:
            scope (PermScopteT): The scope to get permissions for.

        Returns:
            list[Permission]: A list of permissions for this scope.
        """
        return await self.permission_repository.list(scope=scope)
    

    async def get_user_permissions(self, user: UserT) -> list[Permission]:
        """
        Get all permissions for a given user.

        Args:
            user (UserT): The user to get permissions for.

        Returns:
            list[Permission]: A list of permissions for this user.
        """
        return await self.permission_repository.list(user=user)
    

    async def get_user_scopes(self, user: UUID) -> list[PermissionScope]:
        """
        Get use's scopes

        Args:
            user (UserT): The user to get scopes for.

        Returns:
            list[PermissionScope]: A list of scopes for this user.
        """
        return await self.permission_scope_repository.list(permissions__user__id=user)


    async def grant_permission(self, scope_id: UUID, user: UserT) -> Permission:
        """
        Grant permission to a user in a given scope.

        Args:
            scope_id (UUID): The scope to grant permission in.
            user (UserT): The user to grant permission to.

        Returns:
            Permission: The created permission.
        """
        return await self.permission_scope_repository.suscribe_user(scope_id, user)
    

    async def revoke_permission(self, scope_id: UUID, user: UserT) -> Permission | None:
        """
        Revoke permission from a user in a given scope.

        Args:
            scope_id (UUID): The scope to revoke permission in.
            user (UserT): The user to revoke permission from.

        Returns:
            Permission: The deleted permission.
        """
        return await self.permission_scope_repository.unscribe_user(scope_id, user)
    

    async def update_permission(self, permission_id: UUID, data: PermissionUpdate ) -> Permission:
        """
        Update a permission.

        Args:
            permission_id (UUID): The permission to update.
            data (PermissionUpdate): The data to update the permission with.

        Returns:
            Permission: The updated permission.
        """
        permission = await self.permission_repository.get(permission_id)
        await self.permission_repository.update(permission, data.to_dict())


UserServiceType = TypeVar("UserServiceType", bound=BaseUserService)


class UserService(BaseUserService[UserT]):
    """Fimbu user service."""
