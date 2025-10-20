"""
Exceptions submodule
"""

from .http_exceptions import (BaseHttpException,
                            StaticAssetNotFound,
                            AborterException,
                            MissingRequestData,
                            SchemaValidationError,
                            PydanticSchemaValidationError,
                            AuthenticationException,
                            UnauthorizedException,
                            InvalidJWTError,
                            abort,
                            html_abort)

from .runtime_exceptions import (CustomException,
                                 DuplicateRoutePath,
                                DuplicateExceptionHandler,
                                Jinja2NotInitilized,
                                MissingExtension,
                                MissingDependencyInjectionMethod,
                                MissingResponseObject,
                                MissingRouterInstance,
                                InvalidRouteHandler,
                                InvalidWebsocketHandler,
                                MethodNotControllerMethod,
                                UnexpectedDecorator)

from .exception_handler import ExceptionHandler, handles
from werkzeug.exceptions import NotFound, MethodNotAllowed

__all__ = ['CustomException',
            'BaseHttpException',
            'StaticAssetNotFound',
            'AborterException',
            'MissingRequestData',
            'SchemaValidationError',
            'PydanticSchemaValidationError',
            'AuthenticationException',
            'UnauthorizedException',
            "InvalidJWTError",
            'abort',
            'html_abort',
            'DuplicateRoutePath',
            'DuplicateExceptionHandler',
            'Jinja2NotInitilized',
            'MissingExtension',
            'MissingDependencyInjectionMethod',
            'MissingResponseObject',
            'MissingRouterInstance',
            'InvalidRouteHandler',
            'InvalidWebsocketHandler',
            'MethodNotControllerMethod',
            "UnexpectedDecorator",
            "ExceptionHandler",
            "handles",
            "NotFound",
            "MethodNotAllowed"]
