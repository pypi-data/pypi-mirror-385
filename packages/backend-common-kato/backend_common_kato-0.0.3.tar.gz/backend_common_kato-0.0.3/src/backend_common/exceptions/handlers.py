# src/backend_common/exceptions/handlers.py
"""
FastAPI exception handlers.
"""

import logging
from typing import Union
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .base import BaseError
from .http import HTTPError

logger = logging.getLogger(__name__)


async def base_error_handler(request: Request, exc: BaseError) -> JSONResponse:
    """Handle custom BaseError exceptions."""
    logger.error(
        "Application error occurred",
        extra={
            "error_code": exc.error_code.value,
            "message": exc.message,
            "status_code": exc.status_code,
            "context": exc.context,
            "path": request.url.path,
            "method": request.method,
        }
    )

    headers = {}
    if isinstance(exc, HTTPError) and exc.headers:
        headers.update(exc.headers)

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers=headers,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors."""
    logger.warning(
        "Validation error occurred",
        extra={
            "errors": exc.errors(),
            "path": request.url.path,
            "method": request.method,
        }
    )

    # Convert FastAPI validation errors to our format
    field_errors = {}
    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        field_errors[field_name] = error["msg"]

    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "status_code": 422,
            "field_errors": field_errors,
        },
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    logger.warning(
        "HTTP exception occurred",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(
        "Unexpected error occurred",
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "status_code": 500,
        },
    )


def setup_exception_handlers(app) -> None:
    """Setup exception handlers for FastAPI app."""
    app.add_exception_handler(BaseError, base_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
