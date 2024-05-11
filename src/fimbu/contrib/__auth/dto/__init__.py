from litestar.contrib.pydantic import PydanticDTO
from litestar.dto.config import DTOConfig
from fimbu.contrib.auth.utils import get_user_model
from fimbu.contrib.auth.schema import RoleSchema, UserRegistrationSchema, UserSchema, UserRoleSchema

UserModel = get_user_model()


class UserRegistrationDTO(PydanticDTO[UserRegistrationSchema]):
    """User registration DTO."""


class UserReadDTO(PydanticDTO[UserModel]):
    config = DTOConfig(exclude={"password_hash"})


class UserUpdateDTO(PydanticDTO[UserSchema]):
    config = DTOConfig(exclude={"password_hash"}, partial=True)


class RoleCreateDTO(PydanticDTO[RoleSchema]):
    config = DTOConfig(exclude={"id"})


class RoleUpdateDTO(PydanticDTO[UserRoleSchema]):
    config = DTOConfig(exclude={"id"})


class RoleReadDTO(PydanticDTO[RoleSchema]):...
