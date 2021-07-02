import enum

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette import status
from app.schemas.base import ResponseSchemaBase
from app.resources import strings


class ExceptionType(enum.Enum):
    MS_UNAVAILABLE = status.HTTP_500_INTERNAL_SERVER_ERROR, '990', strings.MS_UNAVAILABLE
    MS_INVALID_API_PATH = status.HTTP_500_INTERNAL_SERVER_ERROR, '991', strings.MS_INVALID_API_PATH
    DATA_RESPONSE_MALFORMED = status.HTTP_500_INTERNAL_SERVER_ERROR, '992', strings.DATA_RESPONSE_MALFORMED

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, http_code, code, message):
        self.http_code = http_code
        self.code = code
        self.message = message


class CustomException(Exception):
    http_code: int
    code: str
    message: str

    def __init__(self, http_code: int = None, code: str = None, message: str = None):
        self.http_code = http_code if http_code else status.HTTP_500_INTERNAL_SERVER_ERROR
        self.code = code if code else str(self.http_code)
        self.message = message


async def http_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.http_code,
        content=jsonable_encoder(ResponseSchemaBase().custom_response(exc.code, exc.message))
    )


async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(ResponseSchemaBase().custom_response('400', get_message_validation(exc)))
    )


async def fastapi_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(ResponseSchemaBase().custom_response('500', strings.DATA_RESPONSE_MALFORMED))
    )


def get_message_validation(exc):
    message = ""
    for error in exc.errors():
        message += "/'" + str(error.get("loc")[1]) + "'/" + ': ' + error.get("msg") + ", "

    message = message[:-2]

    return message