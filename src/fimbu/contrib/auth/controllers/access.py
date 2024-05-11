"""User Account Controllers."""

from __future__ import annotations

from typing import Annotated

from litestar import Controller, Request, Response, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.security.jwt import OAuth2Login

from fimbu.conf import settings
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.guards import auth, requires_active_user
from fimbu.contrib.auth.schemas import AccountLogin, AccountRegister, User
from fimbu.contrib.auth.service import UserService
from fimbu.utils.text import slugify
from fimbu.contrib.auth.utils import get_user_model
from fimbu.contrib.auth.utils import get_path


UserModel = get_user_model()


IDENTIFIER_URI = settings.AUTH_UUID_IDENTIFIERS
PREFIX: str = settings.AUTH_PREFIX
USER_DEFAULT_ROLE = settings.AUTH_USER_DEFAULT_ROLE


class AccessController(Controller):
    """User login and registration."""

    tags = ["Access"]
    dependencies = {"users_service": Provide(provide_user_service)}
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
    )
    async def login(
        self,
        users_service: UserService,
        data: Annotated[AccountLogin, Body(title="OAuth2 Login", media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Response[OAuth2Login]:
        """Authenticate a user."""
        user = await users_service.authenticate(data.email, data.password)
        return auth.login(user.email)

    @post(
        operation_id="AccountLogout",
        name="account:logout",
        path=get_path("/login", PREFIX),
        cache=False,
        summary="Logout",
        exclude_from_auth=True,
    )
    async def logout(
        self,
        request: Request,
    ) -> Response:
        """Account Logout"""
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
    )
    async def signup(
        self,
        request: Request,
        users_service: UserService,
        data: AccountRegister,
    ) -> User:
        """User Signup."""
        user_data = data.to_dict()
        role_obj = await users_service.get_role(slug=slugify(USER_DEFAULT_ROLE))
        if role_obj is not None:
            user_data.update({"role_id": role_obj.id})
        user = await users_service.create(user_data)
        request.app.emit(event_id="user_created", user_id=user.id)
        return users_service.to_schema(user, schema_type=User)

    @get(
        operation_id="AccountProfile",
        name="account:profile",
        path=get_path("/profile", PREFIX),
        guards=[requires_active_user],
        summary="User Profile",
        description="User profile information.",
    )
    async def profile(self, request: Request, current_user: UserModel, users_service: UserService) -> User: # type: ignore
        """User Profile."""
        return users_service.to_schema(current_user, schema_type=User)
