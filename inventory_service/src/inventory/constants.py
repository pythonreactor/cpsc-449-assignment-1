from enum import Enum


class InventoryOrderOnEnum(str, Enum):
    Id = 'id'
    Name = 'name'
    Description = 'description'
    CreatedAt = 'created_at'
    UpdatedAt = 'updated_at'
