import json
from http import HTTPStatus
from typing import (
    Dict,
    List,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    root_validator,
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
    page: int = 1
    per_page: int = 25

    @validator('page', pre=True, always=True)
    def validate_page(cls, value):
        return max(1, int(value))

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
    id_in: Optional[Union[List[int], str]] = list()

    @validator('direction', always=True)
    def validate_direction(cls, value):
        """
        Validator to pull the value from the enum choice
        """
        return value.value

    @validator('id_in', always=True)
    def validate_id_in(cls, value):
        """
        Validator to convert the GET str(list) into a List
        """
        if isinstance(value, str):
            return json.loads(value)

        return value


class BaseListResponseSchema(BaseSuccessResponseSchema):
    ...


class BaseDetailQuerySchema(BaseModel):
    id: int


class BaseDetailResponseSchema(BaseSuccessResponseSchema):
    data: Dict = dict()


class BaseDeleteQuerySchema(BaseModel):
    id: Optional[int] = None
    id_in: Optional[Union[List[int], str]] = list()

    @validator('id_in', always=True)
    def validate_id_in(cls, value):
        """
        Validator to convert the GET str(list) into a List
        """
        if isinstance(value, str):
            return json.loads(value)

        return value

    @root_validator(skip_on_failure=True)
    def validate_id(cls, values):
        if values.get('id') and values.get('id_in'):
            raise ValueError('id and id_in cannot be used together')
        elif not values.get('id') and not values.get('id_in'):
            raise ValueError('id or id_in is required')

        return values


class BaseDeleteResponseSchema(BaseSuccessResponseSchema):
    status: int = HTTPStatus.RESET_CONTENT


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
