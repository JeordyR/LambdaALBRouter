import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class HTTPException(Exception):
    code = None
    description = None


class BadRequest(HTTPException):
    code = 400
    description = "400 Bad Request"


class Unauthorized(HTTPException):
    code = 401
    description = "401 Unauthorized"


class Forbidden(HTTPException):
    code = 403
    description = "403 Forbidden"


class NotFound(HTTPException):
    code = 404
    description = "404 Not Found"


class Conflict(HTTPException):
    code = 409
    description = "409 Conflict"


class InternalServerError(HTTPException):
    code = 500
    description = "500 Internal Server Error"


class NotImplemented(HTTPException):
    code = 501
    description = "501 Not Implemented"


class BadGateway(HTTPException):
    code = 502
    description = "502 Bad Gateway"


def catch_exception(f):
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
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


exceptions = {}
is_http_exception = False


def _find_exceptions():
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


def abort(code, message=None):
    if code not in exceptions.keys():
        raise HTTPException(message)
    else:
        raise exceptions[code](message)
