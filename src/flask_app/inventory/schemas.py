from typing import (
    List,
    Optional
)

from pydantic import (
    BaseModel,
    validator
)

from flask_app.base import schemas as base_schemas
from flask_app.inventory import constants as inventory_constants

# region Model schemas


class InventoryObjectSchema(BaseModel):
    id: int
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

    @validator('name', always=True)
    def validate_name(cls, value):
        """
        Validator used to title the name value
        """
        return value.title()

    @validator('category', always=True)
    def validate_category(cls, value):
        """
        Validator used to title the category value
        """
        return value.title()


class InventoryCreateResponseSchema(base_schemas.BaseCreateResponseSchema):
    data: InventoryObjectSchema

# endregion

# region Inventory Bulk Create schemas


class InventoryBulkCreateRequestSchema(BaseModel):
    items: List[InventoryCreateRequestSchema]


class InventoryBulkCreateResponseSchema(base_schemas.BaseBulkCreateResponseSchema):
    data: List[InventoryObjectSchema]

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
    data: List[InventoryObjectSchema]
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
    data: InventoryObjectSchema

# endregion
