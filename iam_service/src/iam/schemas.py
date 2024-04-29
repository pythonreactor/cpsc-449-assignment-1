import datetime
import logging
import os
import re
from typing import (
    Any,
    Dict,
    Optional
)

import bcrypt
from fim import models as base_models
from fim import schemas as base_schemas
from iam import constants as iam_constants
from iam import settings
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    computed_field,
    root_validator,
    validator
)

logger = logging.getLogger(__name__)


# region Model schemas

class AuthTokenModel(base_schemas.BaseModelSchema):
    """
    Base schema for the AuthToken model
    """
    key: str = Field(
        default_factory=lambda: bcrypt.hashpw(os.urandom(64), bcrypt.gensalt()).decode('utf-8'),
        frozen=True
    )
    updated_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)

    @computed_field
    @property
    def expired(self) -> bool:
        current_time = datetime.datetime.utcnow()
        timeout_hours = settings.MAX_TOKEN_AGE_SECONDS / (60 ** 2)
        token_age = current_time - self.updated_at

        if token_age > datetime.timedelta(hours=timeout_hours):
            logger.warning('User auth token has expired.')
            return True

        return False


class UserModel(base_models.BasePKFlaskModel):
    """
    Base schema for the User model.
    """
    email: EmailStr
    username: str
    first_name: str
    last_name: str

    is_superuser: bool = False
    password: Optional[Any] = Field(..., frozen=True, repr=False)

    auth_token: Optional[AuthTokenModel] = Field(None, alias='token')

    @validator('password', pre=True, always=True)
    def hash_password(cls, value: Any) -> str:
        password_hash_regex = r'^\$2[abxy]\$\d{2}\$[./0-9A-Za-z]{53}$'

        if value:
            # Because we pass the `password` back in on each save, we don't want to force
            # a re-hashing of the hashed version of a password
            if not re.match(password_hash_regex, value):
                return bcrypt.hashpw(str(value).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return value

        return None

    @validator('first_name', pre=True, always=True)
    def validate_first_name(cls, value):
        """
        Validator used to title the first_name value
        """
        return value.title()

    @validator('last_name', pre=True, always=True)
    def validate_last_name(cls, value):
        """
        Validator used to title the last_name value
        """
        return value.title()

    def model_dump(self, override: bool = True, additional: set = None, **kwargs):
        """
        Override base Pydantic model_dump method to include only
        the field's we'd want to return if `include` is not provided.
        """
        if override:
            kwargs['include'] = {field.alias if field.alias else name for name, field in UserObjectResponseSchema.__fields__.items()}

        return super().model_dump(**kwargs)

# endregion


# region Response Model schemas

class UserObjectResponseSchema(BaseModel):
    id: int = Field(..., alias='pk', serialization_alias='id')
    first_name: str
    last_name: str
    email: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

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
        from iam.models import User

        value         = value.lower()
        existing_user = User.query.find_by_email(value)

        if existing_user:
            raise ValueError(f'A user with the email {value} already exists')

        return value

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


class LoginResponseSchema(base_schemas.BaseSuccessResponseSchema):
    email: str
    token: str

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
    data: list[UserObjectResponseSchema]
    pagination: base_schemas.BasePaginationResponseSchema

# endregion


# region User Detail schemas

class UserDetailQuerySchema(base_schemas.BaseDetailQuerySchema):
    ...


class UserDetailRequestSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @validator('first_name', always=True)
    def validate_first_name(cls, value):
        """
        Validator used to title the first_name value
        """
        if value:
            return value.title()

    @validator('last_name', always=True)
    def validate_last_name(cls, value):
        """
        Validator used to title the last_name value
        """
        if value:
            return value.title()


class UserDetailResponseSchema(base_schemas.BaseDetailResponseSchema):
    data: UserObjectResponseSchema

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


# region External service schemas

class ExternalAuthenticationResponseSchema(base_schemas.BaseSuccessResponseSchema):
    user: Dict[str, Any]
    token: Dict[str, Any]

# endregion
