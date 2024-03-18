from enum import Enum


class UserOrderOnEnum(str, Enum):
    Id = 'id'
    Email = 'email'
    Username = 'username'
    FirstName = 'first_name'
    LastName = 'last_name'
    CreatedAt = 'created_at'
    UpdatedAt = 'updated_at'
