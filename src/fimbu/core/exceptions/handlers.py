from litestar import Request, Response
from edgy.exceptions import ObjectNotFound, EdgyException
from fimbu.core.exceptions import FimbuException



def core_handle_exceptions(request: Request, exception: Exception) -> None:
    """Handle database exceptions."""

    response = None

    if isinstance(exception, ObjectNotFound):
        response = Response(
            content={"detail": "Object not found"},
            status_code=404,
        )
    
    elif isinstance(exception, (FimbuException, EdgyException)):
        response = Response(
            content={"detail": "Internal server error"},
            status_code=500,
        )

    return response
