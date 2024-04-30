from litestar.contrib.pydantic import PydanticDTO
from litestar.dto.config import DTOConfig
from fimbu.contrib.auth.utils import get_user_model
from fimbu.contrib.auth.schema import UserRegistrationSchema

UserModel = get_user_model()


class UserRegistrationDTO(PydanticDTO[UserRegistrationSchema]):
    """User registration DTO."""


class UserReadDTO(PydanticDTO[UserModel]):
    config = DTOConfig(exclude={"password_hash"})


class UserUpdateDTO(PydanticDTO[UserModel]):
    config = DTOConfig(exclude={"password_hash"}, partial=True)
