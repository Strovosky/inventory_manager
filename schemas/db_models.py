# This module will be in charge of creating the database models.

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date , BigInteger, ForeignKey
from datetime import datetime, date
from config.db_config import engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from security.password_encript import password_hasher
from models.pydantic_models import FullEmployee


Base = declarative_base()

local_session = sessionmaker()(bind=engine)

# This table will keep a record of the employees and their positions to know what access to grant.
class Employees(Base):
    __tablename__= "Employees"
    employee_id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    first_name = Column(String(length=100), nullable=False, unique=False)
    last_name = Column(String(length=150), nullable=False, unique=False)
    username = Column(String(length=70), nullable=False, unique=True)
    cellphone = Column(BigInteger, unique=True, nullable=True)
    email = Column(String(length=150), unique=True, nullable=True)
    position = Column(String(length=50), unique=False, nullable=False)
    password = Column(String(length=200), nullable=False, unique=False)

# This table will keep a record of the company products.
# It will contain some general info about the product and other specific info that will depend 
# on the tables product reception, product sale and product spoiled to update it.
class Products(Base):
    __tablename__= "Products"
    product_id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    product_name = Column(String(length=100), nullable=False, unique=True)
    description = Column(String(length=300), nullable=True, unique=False)
    brand = Column(String(length=100), nullable=False, unique=False)
    category = Column(String(length=100), nullable=False, unique=False)
    purchase_price = Column(Integer, nullable=False, unique=False)
    sale_price = Column(Integer, nullable=False, unique=False)

    # This is affected by ProductsReceived/ProductsSold/SpoiledProducts/ReturnedProducts
    quantity_in_stock = Column(Integer, nullable=False, unique=False, default=0)

    # This one is affected by ProductsSold
    quantity_sold = Column(Integer, nullable=False, unique=False, default=0)

    # This one is affected by SpoiledProducts
    quantity_spoiled = Column(Integer, nullable=False, unique=False, default=0)

    # This one is affected by quantity_in_stock.
    status = Column(String(length=9), nullable=False, unique=False, default="in_stock") # Enum: in_stock/sold_out
    
    # This one can only be set by a Manager.
    on_sale = Column(Boolean, default=False)

# This table will contain which products have arrived to the warehouse.
class ProductsReceived(Base):
    __tablename__= "ProductsReceived"
    reception_number = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("Products.product_id"))
    quantity = Column(Integer, nullable=False, unique=False)
    date_arrived = Column(DateTime, default=datetime.utcnow, nullable=False)
    note = Column(String(length=300), nullable=True, unique=False, default=None)

# This table will store which products have been sold.
class ProductsSold(Base):
    __tablename__= "ProductsSold"
    sale_number = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("Products.product_id"))
    quantity = Column(Integer, nullable=False, unique=False)
    date_sold = Column(DateTime, default=datetime.utcnow, nullable=False, unique=False)
    note = Column(String(length=300), nullable=True, unique=False, default=None)

# This class will let us know how many products have gotten spoiled or damaged.
class SpoiledProducts(Base):
    __tablename__= "SpoiledProducts"
    spoiled_registration = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("Products.product_id"))
    quantity = Column(Integer, nullable=False, unique=False)
    date_expired = Column(Date, nullable=False, unique=False, default=date.today)
    note = Column(String(length=300), nullable=True, unique=False)

# This class will update info about the products if they've been returned by the customer.
class ReturnedProducts(Base):
    __tablename__= "ReturnedProducts"
    return_registration = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("Products.product_id"))
    quantity = Column(Integer, nullable=False, unique=False)
    date_returned = Column(DateTime, default=datetime.utcnow, nullable=True, unique=False)
    note = Column(String(length=300), nullable=True, unique=False)


Base.metadata.create_all(engine)

if len(local_session.query(Employees).all()) == 0:
    manager_pydantic = FullEmployee(
        first_name=config("MANAGER_FIRST_NAME"),
        last_name=config("MANAGER_LAST_NAME"),
        username=config("MANAGER_USERNAME"),
        cellphone=config("MANAGER_CELLPHONE"),
        email=config("MANAGER_EMAIL"),
        position=config("MANAGER_POSITION"),
        password=password_hasher(config("MANAGER_PASSWORD"))
    )
    first_manager = Employees(
        first_name=manager_pydantic.first_name,
        last_name=manager_pydantic.last_name,
        username=manager_pydantic.username,
        cellphone=manager_pydantic.cellphone,
        email=manager_pydantic.email,
        position=manager_pydantic.position.value,
        password=manager_pydantic.password)

    local_session.add(first_manager)
    local_session.commit()
