# In this module, I'll create the employees, the new products, and new product_receptions. 

from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum


class Positions(Enum):
    Cashier = "Cashier"
    Clerk = "Clerk"
    Manager = "Manager"

class Categories(Enum):
    Vegetables = "Vegetables"
    Dairy = "Dairy"
    Fruit = "Fruit"
    Alcohol = "Alcohol"
    Grains = "Grains"
    Candy = "Candy"
    Cereal = "Cereal"
    Canned_Food = "Canned_Food"
    Spices = "Spices"
    Oil = "Oil"
    Others = "Others"

# This one will be commonly used as a response_model.
class BaseEmployee(BaseModel):
    first_name: str = Field(..., max_length=60)
    last_name: str = Field(..., max_length=70)
    username: str = Field(..., max_length=70)
    position: Positions = Field(..., example="Cashier/Clerk/Manager")
    cellphone: Optional[int] = Field(default=None, gt=999999999, lt=10000000000)
    email: Optional[EmailStr] = Field(default=None)

# This will be the response model to show employees to the managers.
class EmployeeOut(BaseEmployee):
    employee_id: int = Field(...)

# This one will be used to create a new employee.
class FullEmployee(BaseEmployee):
    password: str = Field(..., min_length=8, max_length=100)


class BaseProduct(BaseModel):
    name: str = Field(..., max_length=100)
    brand: str = Field(default=None, max_length=100)
    description: str = Field(default=None, max_length=300)
    category: Categories = Field(...)
    purchase_prise: int = Field(...)
    sale_price: int = Field(...)


class Reception(BaseModel):
    product_id: int = Field(..., description="The id of the product we receive.")
    quantity: int = Field(..., description="The quantity of products we received.")
    note: str = Field(default=None, max_length=300)

class Sale(Reception):
    pass

class Spoiled(Reception):
    date_expired: date = Field(...)

class Returned(Reception):
    is_spoiled: bool = Field(default=False)
