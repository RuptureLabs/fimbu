from __future__ import annotations 
from typing import TYPE_CHECKING, Tuple, Any

import configparser
import os
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
    PermissionDeniedException,
)
from fimbu.core.exceptions import (
    ApplicationError,
    AuthorizationError,
    _HTTPConflictException,
)
from fimbu.db.exceptions import ObjectNotFound, DuplicateRecordError, RepositoryError
from litestar.middleware.exceptions._debug_response import create_debug_response
from litestar.middleware.exceptions.middleware import create_exception_response

if TYPE_CHECKING:
    from pydantic import BaseModel, Field
    from litestar.middleware.exceptions.middleware import ExceptionResponseContent
    from litestar.connection import Request
    from litestar.response import Response


def load_init_settings() -> configparser.ConfigParser:
    """
    This is used the first time settings are needed, if the user hasn't
    configured settings manually.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.curdir, "fimbu.ini")

    if os.path.exists(path):
        config.read(path)
    else:
        config['default'] = {
            'settings': 'fimbu.conf.global_settings',
        }
    return config


def is_fimbu_project() -> bool:
    """A fimbu project is specified by having fimbu.ini in the current directory"""
    return os.path.exists(os.path.join(os.curdir, 'fimbu.ini'))


def setup_fimbu():
    """
    This is used the first time settings are needed, if the user hasn't
    configured settings manually.
    """
    config = load_init_settings()
    os.environ.setdefault('FIMBU_SETTINGS_MODULE', config['default']['settings'])
    
    if is_fimbu_project():
        import sys
        sys.path.append(os.path.abspath(os.curdir))


def get_pydantic_fields(model: BaseModel) -> Tuple[dict[str, Field], dict[str, Field]]:
    """
    Get the fields from a pydantic model.

    Args:
        model: A pydantic model
    Returns:
        A tuple of (required_fields, optionnal_fields)

    """
    fields = model.model_fields
    required_fields = {}
    optionnal_fields = {}

    for field_name, field in fields.items():
        if field.is_required():
            required_fields[field_name] = field
        else:
            optionnal_fields[field_name] = field
    return required_fields, optionnal_fields


def exception_to_http_response(
    request: Request[Any, Any, Any],
    exc: ApplicationError | RepositoryError,
) -> Response[ExceptionResponseContent]:
    """Transform repository exceptions to HTTP exceptions.

    Args:
        request: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns:
        Exception response appropriate to the type of original exception.
    """
    http_exc: type[HTTPException]
    if isinstance(exc, ObjectNotFound):
        http_exc = NotFoundException
    elif isinstance(exc, DuplicateRecordError | RepositoryError):
        http_exc = _HTTPConflictException
    elif isinstance(exc, AuthorizationError):
        http_exc = PermissionDeniedException
    else:
        http_exc = InternalServerException
    if request.app.debug and http_exc not in (PermissionDeniedException, ObjectNotFound, AuthorizationError):
        return create_debug_response(request, exc)
    return create_exception_response(request, http_exc(detail=str(exc.__cause__)))
