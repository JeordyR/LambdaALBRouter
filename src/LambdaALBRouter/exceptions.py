"""
LambdaALBRouter.exceptions

Implements a set of Python exceptions for HTTP statuses that can be raised with associated codes and descriptions.
Implements a decorator to handle all exceptions and convert them into valid responses for ALB.
Implements an abort function for easy exiting of exec functions that returns a valid response to ALB.

Usage:
    from .execptions import *

    @catch_exception
    def my_function(data):
        if not data:
            abort(400, "Missing 'data' parameter")

"""

import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class HTTPException(Exception):
    """
    Base class used for all HTTP exceptions. Used to help find the subclasses.
    Will return as an InternalServerError if raised directly.
    """
    code = None
    description = None


class BadRequest(HTTPException):
    """
    400 Bad Request, raised if the user sends something the application can not handle.
    """
    code = 400
    description = "400 Bad Request"


class Unauthorized(HTTPException):
    """
    401 Unauthorized, raised if the user is not authorized to access the requested resource
    """
    code = 401
    description = "401 Unauthorized"


class Forbidden(HTTPException):
    """
    403 Forbidden, raised if the requested resource is forbidden from the authenticated user
    """
    code = 403
    description = "403 Forbidden"


class NotFound(HTTPException):
    """
    404 Not Found, raised if the requested resource does not exist
    """
    code = 404
    description = "404 Not Found"


class Conflict(HTTPException):
    """
    409 Conflict, raised when a request cannot be completed because it conflicts with the current state of the server
    """
    code = 409
    description = "409 Conflict"


class InternalServerError(HTTPException):
    """
    500 InternalServerError, raised to note a general error on the server-side while processing the request
    """
    code = 500
    description = "500 Internal Server Error"


class NotImplemented(HTTPException):
    """
    501 NotImplemented, raised when the requested resource is planned, but not yet implemented
    """
    code = 501
    description = "501 Not Implemented"


class BadGateway(HTTPException):
    """
    502 BadGateway, raised when an upstream server gets an invalid response from a request
    """
    code = 502
    description = "502 Bad Gateway"


def catch_exception(f):
    """
    Decorator that catches all exceptions and converts them into standard dictionary responses for ALB
    """
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Check if the raised exception has a code and description value, use those in response
            if "code" in e.__dir__() and "description" in e.__dir__():
                logger.error(f"Coded Error in {f.__name__}: {str(e)}")
                return {
                    "statusCode": e.code,
                    "statusDescription": e.description,
                    "isBase64Encoded": False,
                    "headers": {
                        "Content-Type": "text/plain"
                    },
                    "body": str(e)
                }
            else:
                logger.error(f"Error in {f.__name__}: {str(e)}")
                return {
                    "statusCode": 500,
                    "statusDescription": "Server Error",
                    "isBase64Encoded": False,
                    "headers": {
                        "Content-Type": "text/plain"
                    },
                    "body": str(e)
                }
    return func

# Find all HTTP exceptions implemented in this module and map their code to the exception
exceptions = {}
is_http_exception = False


def _find_exceptions():
    """
    Loops through all global times in the module and finds subclasses of HTTPException
    When located, store them as a mapping to their HTTP status code
    """
    for _name, obj in globals().items():
        try:
            is_http_exception = issubclass(obj, HTTPException)
        except TypeError:
            is_http_exception = False
        if not is_http_exception:
            continue
        if obj.code is None:
            continue

        exceptions[obj.code] = obj


_find_exceptions()
del _find_exceptions


def abort(code: str, message: str = None) -> None:
    """
    Simple function to allow easy error throwing from app routes. Takes the code and message and raises
    an appropriate exception based on that code, passing the message through.

    This function is only intended for use with throwing json errors currently.

    :param code: HTTP code to use in the response
    :param message: Message to include in the response
    """
    if code not in exceptions.keys():
        raise HTTPException(message)
    else:
        raise exceptions[code](message)
