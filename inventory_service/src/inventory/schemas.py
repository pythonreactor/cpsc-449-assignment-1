from typing import (
    List,
    Optional
)

from fim import models as base_models
from fim import schemas as base_schemas
from inventory import constants as inventory_constants
from inventory import settings
from pydantic import (
    BaseModel,
    Field,
    validator
)

logger = settings.getLogger(__name__)


# region Model schemas

class InventoryModel(base_models.BasePKFlaskModel):
    """
    Base schema for the Inventory model.
    """
    name: str
    category: str

    weight: float
    price: float

    user_id: Optional[base_schemas.FIMObjectID] = None

    @validator('name', always=True)
    def validate_name(cls, value):
        """
        Validator used to title the name value
        """
        return value.title()

    @validator('category', pre=True, always=True)
    def validate_category(cls, value):
        """
        Validator used to title the category value
        """
        return value.title()

    @validator('weight', pre=True, always=True)
    def validate_weight(cls, value):
        """
        Validator used to round the weight value to 5 decimal places
        """
        return float(f'{float(value):.5f}')

    @validator('price', pre=True, always=True)
    def validate_price(cls, value):
        """
        Validator used to round the price value to 2 decimal places
        """
        return float(f'{float(value):.2f}')

    def model_dump(self, override: bool = True, **kwargs):
        """
        Override base Pydantic model_dump method to include only
        the field's we'd want to return if `include` is not provided.
        """
        if override:
            if not kwargs.get('include', None):
                kwargs['include'] = {field.alias if field.alias else name for name, field in InventoryObjectResponseSchema.__fields__.items()}

        return super().model_dump(**kwargs)

# endregion


# region Response Model schemas

class InventoryObjectResponseSchema(BaseModel):
    id: int = Field(..., alias='pk', serialization_alias='id')
    name: str
    category: str
    weight: float
    price: float

# endregion


# region Inventory Create schemas

class InventoryCreateRequestSchema(BaseModel):
    name: str
    category: str
    weight: Optional[float]
    price: Optional[float]


class InventoryCreateResponseSchema(base_schemas.BaseCreateResponseSchema):
    data: InventoryObjectResponseSchema

# endregion


# region Inventory Bulk Create schemas

class InventoryBulkCreateRequestSchema(BaseModel):
    items: List[InventoryCreateRequestSchema]


class InventoryBulkCreateResponseSchema(base_schemas.BaseBulkCreateResponseSchema):
    data: List[InventoryObjectResponseSchema]

# endregion


# region Inventory Delete schemas

class InventoryDeleteQuerySchema(base_schemas.BaseDeleteQuerySchema):
    ...


class InventoryDeleteResponseSchema(base_schemas.BaseDeleteResponseSchema):
    ...

# endregion


# region Inventory Bulk Delete schemas

class InventoryBulkDeleteRequestSchema(base_schemas.BaseBulkDeleteRequestSchema):
    ...


class InventoryBulkDeleteResponseSchema(base_schemas.BaseBulkDeleteResponseSchema):
    ...

# endregion


# region Inventory Search schemas

class InventorySearchQuerySchema(base_schemas.BaseSearchQuerySchema):
    name: str = Field(None, description='Items with "name" containing or matching the string')
    category: str = Field(None, description='Items with "category" containing or matching the string')


class InventorySearchResponseSchema(base_schemas.BaseSearchResponseSchema):
    data: List[InventoryObjectResponseSchema]
    pagination: base_schemas.BasePaginationResponseSchema

# endregion


# region Inventory List schemas

class InventoryListQuerySchema(base_schemas.BaseListQuerySchema):
    order_by: inventory_constants.InventoryOrderOnEnum = inventory_constants.InventoryOrderOnEnum.Id

    @validator('order_by', always=True)
    def validate_order_by(cls, value):
        """
        Validator to pull the value from the enum choice
        """
        return value.value


class InventoryListResponseSchema(base_schemas.BaseListResponseSchema):
    data: List[InventoryObjectResponseSchema]
    pagination: base_schemas.BasePaginationResponseSchema

# endregion


# region Inventory Detail schemas

class InventoryDetailQuerySchema(base_schemas.BaseDetailQuerySchema):
    ...


class InventoryDetailRequestSchema(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    weight: Optional[float] = None
    price: Optional[float] = None

    @validator('name', always=True)
    def validate_name(cls, value):
        """
        Validator used to title the name value
        """
        if value:
            return value.title()

    @validator('category', always=True)
    def validate_category(cls, value):
        """
        Validator used to title the category value
        """
        if value:
            return value.title()


class InventoryDetailResponseSchema(base_schemas.BaseDetailResponseSchema):
    data: InventoryObjectResponseSchema

# endregion
