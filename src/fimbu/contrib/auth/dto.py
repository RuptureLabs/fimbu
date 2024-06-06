from __future__ import annotations

from litestar.dto.msgspec_dto import MsgspecDTO
from litestar.dto import DTOConfig

from fimbu.contrib.auth.schemas import User, PermissionScope


class CreateUserDTO(MsgspecDTO[User]):
    config = DTOConfig(
        exclude={'joined_at', 'id', 'verified_at',},
    )


class UpdateUserDTO(MsgspecDTO[User]):
    config = DTOConfig(
        exclude={'joined_at', 'id', 'verified_at',},
        partial=True,
    )


class PermissionScopeUpdateDTO(MsgspecDTO[PermissionScope]):
    config = DTOConfig(
        exclude={'codename', 'slug',},
    )
