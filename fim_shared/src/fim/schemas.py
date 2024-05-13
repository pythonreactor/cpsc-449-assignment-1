import datetime
import json
from http import HTTPStatus
from typing import (
    Dict,
    List,
    Optional,
    Union
)

from bson import ObjectId
from fim.constants import SortDirectionEnum
from pydantic import (
    BaseModel,
    Field,
    validator
)

# region Base Model schemas

class FIMObjectID(ObjectId):
    """
    Custom pydantic type for MongoDB ObjectId
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type='string')

    @classmethod
    def validate(cls, value, values, **kwargs):
        if not ObjectId.is_valid(value):
            raise ValueError('Invalid ObjectId')

        if isinstance(value, ObjectId):
            if not isinstance(value, cls):
                return cls(value)
            else:
                return value
            return cls(value)

        return ObjectId(value)


class BaseModelSchema(BaseModel):
    """
    Base schema for Flask models
    """
    id: Optional[FIMObjectID] = Field(None, alias='_id', exclude=True)

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: Optional[datetime.datetime] = None

    def model_dump(self, override: bool = False, **kwargs):
        return super().model_dump(**kwargs)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

        from_attributes = True
        validate_assignment = True
        json_encoders = {FIMObjectID: str}


class BasePKModelSchema(BaseModelSchema):
    pk: Optional[int] = None

# endregion


# region Base Response schemas

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


class BaseCreateResponseSchema(BaseSuccessResponseSchema):
    status: int = HTTPStatus.CREATED
    data: Dict = dict()


class BaseBulkCreateResponseSchema(BaseSuccessResponseSchema):
    status: int = HTTPStatus.CREATED
    data: List[Dict] = list(dict())


class BaseSearchQuerySchema(BasePaginationSchema):
    ...

    @validator('*', pre=True)
    def force_lowercase(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class BaseSearchResponseSchema(BaseSuccessResponseSchema):
    ...


class BaseListQuerySchema(BasePaginationSchema):
    direction: SortDirectionEnum = SortDirectionEnum.Ascending
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


class BaseBulkDeleteRequestSchema(BaseModel):
    ids: List[int]

    @validator('ids', always=True)
    def validate_ids(cls, value):
        """
        Validator to convert the GET str(list) into a List
        """
        if isinstance(value, str):
            return json.loads(value)

        return value


class BaseBulkDeleteResponseSchema(BaseSuccessResponseSchema):
    status: int = HTTPStatus.RESET_CONTENT


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
