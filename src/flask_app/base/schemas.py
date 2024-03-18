from http import HTTPStatus
from typing import Optional

from pydantic import (
    BaseModel,
    validator
)

from flask_app.base import constants as base_constants

# region Base schemas

class BaseSuccessResponseSchema(BaseModel):
    success: bool = True
    message: str = ''
    status: int = HTTPStatus.OK


class BaseErrorResponseSchema(BaseModel):
    success: bool = False
    message: str = ''
    status: int = HTTPStatus.BAD_REQUEST


class BasePaginationSchema(BaseModel):
    page: int = 0
    per_page: int = 25

    @validator('page', pre=True, always=True)
    def validate_page(cls, value):
        return max(0, int(value))

    @validator('per_page', pre=True, always=True)
    def validate_per_page(cls, value):
        return max(1, min(100, int(value)))


class BasePaginationResponseSchema(BaseModel):
    total: int
    pages: int
    next_page: Optional[int]
    prev_page: Optional[int]


class BaseListQuerySchema(BasePaginationSchema):
    direction: base_constants.SortDirectionEnum = base_constants.SortDirectionEnum.Ascending
    order_by: Optional[str] = ''

    @validator('direction', always=True)
    def validate_direction(cls, value):
        """
        Validator to pull the value from the enum choice
        """
        return value.value


class BaseListResponseSchema(BaseSuccessResponseSchema):
    ...


class BaseDetailQuerySchema(BaseModel):
    id: int

# endregion


# region Response schemas by status code

class BadRequestResponseSchema(BaseErrorResponseSchema):
    status: int = HTTPStatus.BAD_REQUEST


class UnauthorizedResponseSchema(BaseErrorResponseSchema):
    message: str = 'unauthorized'
    status: int = HTTPStatus.UNAUTHORIZED


class NotFoundResponseSchema(BaseErrorResponseSchema):
    status: int = HTTPStatus.NOT_FOUND


class InternalServerErrorResponseSchema(BaseErrorResponseSchema):
    message: str = 'internal server error'
    status: int = HTTPStatus.INTERNAL_SERVER_ERROR

# endregion
