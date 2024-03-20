from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    root_validator,
    validator
)

from flask_app.base import schemas as base_schemas
from flask_app.iam import constants as iam_constants
from flask_app.iam import models as iam_models

# region Model schemas


class AuthTokenSchema(BaseModel):
    email: str
    token: str


class UserObjectSchema(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str

# endregion

# region Signup schemas


class SignupRequestSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str

    @validator('email', always=True)
    def validate_email(cls, value):
        """
        Validator to normalize the email value and check if a user
        with the email already exists
        """
        value = value.lower()
        existing_user = iam_models.User.query.filter_by(email=value).first()

        if existing_user:
            raise ValueError(f'a user with the email {value} already exists')

        return value

    @validator('first_name', always=True)
    def validate_first_name(cls, value):
        """
        Validator used to title the first_name value
        """
        return value.title()

    @validator('last_name', always=True)
    def validate_last_name(cls, value):
        """
        Validator used to title the last_name value
        """
        return value.title()

    @root_validator(pre=True)
    def validate_password(cls, values):
        """
        Validate that the password and confirm_password values match.
        """
        if values.get('password') != values.get('confirm_password'):
            raise ValueError('passwords must match')

        values['username'] = values['email']

        return values


class SignupResponseSchema(base_schemas.BaseSuccessResponseSchema):
    status: int = 201

# endregion

# region Login schemas


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str

    @validator('email', always=True)
    def validate_email(cls, value):
        """
        Validator to normalize the email value
        """
        return value.lower()


class LoginResponseSchema(base_schemas.BaseSuccessResponseSchema, AuthTokenSchema):
    ...

# endregion

# region User List schemas


class UserListQuerySchema(base_schemas.BaseListQuerySchema):
    order_by: iam_constants.UserOrderOnEnum = iam_constants.UserOrderOnEnum.Id

    @validator('order_by', always=True)
    def validate_order_by(cls, value):
        """
        Validator to pull the value from the enum choice
        """
        return value.value


class UserListResponseSchema(base_schemas.BaseListResponseSchema):
    data: list[UserObjectSchema]
    pagination: base_schemas.BasePaginationResponseSchema

# endregion

# region User Detail schemas


class UserDetailQuerySchema(base_schemas.BaseDetailQuerySchema):
    ...


class UserDetailRequestSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]

    @validator('first_name', always=True)
    def validate_first_name(cls, value):
        """
        Validator used to title the first_name value
        """
        return value.title()

    @validator('last_name', always=True)
    def validate_last_name(cls, value):
        """
        Validator used to title the last_name value
        """
        return value.title()


class UserDetailResponseSchema(base_schemas.BaseDetailResponseSchema):
    data: UserObjectSchema

# endregion

# region User Delete schemas


class UserDeleteQuerySchema(base_schemas.BaseDeleteQuerySchema):
    ...


class UserDeleteResponseSchema(base_schemas.BaseDeleteResponseSchema):
    ...

# endregion

# region User Bulk Delete schemas


class UserBulkDeleteRequestSchema(base_schemas.BaseBulkDeleteRequestSchema):
    ...


class UserBulkDeleteResponseSchema(base_schemas.BaseBulkDeleteResponseSchema):
    ...

# endregion
