"""User Account Controllers."""

from __future__ import annotations

from typing import Annotated, Any, cast

from litestar import Controller, Request, Response, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.security.session_auth import SessionAuth
from litestar.security.jwt import OAuth2Login
from litestar.contrib.jwt import JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException

from fimbu.conf import settings
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.guards import requires_active_user
from fimbu.contrib.auth.schemas import AccountLogin, AccountRegister, User
from fimbu.contrib.auth.protocols import UserT, UserProtocol
from fimbu.core.exceptions import ImproperlyConfiguredException
from fimbu.contrib.auth.service import UserService, UserServiceType
from fimbu.contrib.base import Message
from fimbu.utils.text import slugify
from fimbu.contrib.auth.utils import get_user_model, get_auth_backend, user_is_verified
from fimbu.contrib.auth.utils import get_path


UserModel = get_user_model()


PREFIX: str = settings.AUTH_PREFIX
USER_DEFAULT_ROLE = settings.USER_DEFAULT_ROLE


class AccessController(Controller):
    """User login and registration."""

    tags = ["Auth - Access"]
    dependencies = {"service": Provide(provide_user_service)}
    signature_namespace = {
        "UserService": UserService,
        "OAuth2Login": OAuth2Login,
        "RequestEncodingType": RequestEncodingType,
        "Body": Body,
        "User": User,
    }

    @post(
        operation_id="AccountLogin",
        name="account:login",
        path=get_path("/login", PREFIX),
        cache=False,
        summary="Login",
        exclude_from_auth=True,
        exclude_from_csrf=True,
    )
    async def login(
        self,
        request: Request[User, Any, Any],
        service: UserServiceType,
        data: Annotated[AccountLogin, Body(title="OAuth2 Login", media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Any:
        """Authenticate a user."""

        auth_backend = get_auth_backend(request.app)

        if isinstance(auth_backend, (JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth)):
            return await self.login_jwt(data, service, request, auth_backend)
        elif isinstance(auth_backend, SessionAuth):
            return await self.login_session(data, service, request)
        else:
            raise ImproperlyConfiguredException("login can only be used with JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth or SessionAuth")

    @post(
        operation_id="AccountLogout",
        name="account:logout",
        path=get_path("/logout", PREFIX),
        cache=False,
        summary="Logout",
        exclude_from_auth=True,
    )
    async def logout(
        self,
        request: Request,
    ) -> Response[Message]:
        """Account Logout"""
        auth = get_auth_backend(request.app)
        request.cookies.pop(auth.key, None)
        request.clear_session()

        response = Response(
            {"message": "OK"},
        status_code=200,

        )
        response.delete_cookie(auth.key)

        return response

    @post(
        operation_id="AccountRegister",
        name="account:register",
        path=get_path("/signup", PREFIX),
        cache=False,
        summary="Create User",
        description="Register a new account.",
        exclude_from_auth=True,
        exclude_from_csrf=True,
    )
    async def signup(
        self,
        request: Request,
        service: UserServiceType,
        data: AccountRegister,
    ) -> User:
        """User Signup."""
        user_data = data.to_dict()

        user = await service.register(user_data)
        role_obj = await service.get_role(slug=slugify(USER_DEFAULT_ROLE))
        if role_obj is not None:
            await service.assign_role(user, role_obj)
        return service.to_schema(user, schema_type=User)

    @get(
        operation_id="AccountProfile",
        name="account:profile",
        path=get_path("/profile", PREFIX),
        guards=[requires_active_user],
        summary="User Profile",
        description="User profile information.",
    )
    async def profile(self, request: Request[User, Any, Any], service: UserServiceType) -> User: # type: ignore
        """User Profile."""
        current_user = await service.get_user(request.user.id)
        return service.to_schema(current_user, schema_type=User)


    async def login_jwt(self, 
        data: AccountRegister,
        service: UserServiceType, 
        request: Request,
        auth_backend: JWTAuth | JWTCookieAuth | OAuth2PasswordBearerAuth | None = None) -> Response[OAuth2Login]:

        user = await service.authenticate(data, request)
        if user is None:
            raise NotAuthorizedException(detail="login failed, invalid input")

        if not user_is_verified(user):
            raise PermissionDeniedException(detail="User not verified")
        
        if user.is_active is False:
            raise PermissionDeniedException(detail="User not active")
        
        return auth_backend.login(identifier=str(user.id), send_token_as_response_body=True)
    

    async def login_session(self,
        data: AccountLogin,
        service: UserServiceType, 
        request: Request
        ) -> UserT:
        user = await service.authenticate(data, request)
        if user is None:
            request.clear_session()
            raise NotAuthorizedException(detail="login failed, invalid input")

        if not user_is_verified(user):
            raise PermissionDeniedException(detail="User not verified")
        
        if user.is_active is False:
            raise PermissionDeniedException(detail="User not active")

        request.set_session({"user_id": user.id})
        return service.to_schema(user, schema_type=User)
