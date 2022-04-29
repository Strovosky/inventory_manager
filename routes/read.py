# In this module, I will create all the read type enpoints.

from fastapi import APIRouter, Depends, HTTPException, status
from security.jwt_handler import clerk_verifier, oauth2_scheme, token_validator, manager_verifier
from models.pydantic_models import EmployeeOut
from schemas.db_models import Employees, Products, ProductsReceived, local_session


app_read = APIRouter()


@app_read.get(
    path="/get-all-employees",
    summary="ONLY MANAGER ACCESS: This endpoint will return all the employees.",
    tags=["Employees"]
)
def all_employees(token: str = Depends(oauth2_scheme)):
    """
    ***ALL EMPLOYEES***

    This endpoint will let any MANAGER see all the info of the employees.

    Parameters:
    - ***token***: str - Depends

    Returns list with all the info of the employees.
    """
    
    if token_validator(token) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token")
    
    if manager_verifier(token) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This employee is not authorized.")

    all_employees_db = local_session.query(Employees).all()

    all_employees_pydantic = {}

    for ind, employee in enumerate(all_employees_db, start=1):
        temporary_employee = EmployeeOut(
            employee_id=employee.employee_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            username=employee.username,
            position=employee.position,
            cellphone=employee.cellphone,
            email=employee.email)
        all_employees_pydantic.update({f"Employee {ind}": temporary_employee})

    return all_employees_pydantic

#####################################################################
#####################################################################

@app_read.get(
    path="/all-products",
    summary="ALL EMPLOYEES ACCESS: This endpoint will let you see all the products.",
    tags=["Products"])
def get_all_products(token: str = Depends(oauth2_scheme)):
    """
    ***GET ALL PRODUCTS***

    This endpoint will show relevant info of the products registered.

    Parameters:
    - ***token***: str - Depends

    Returns a list with all the products registered.
    """
    if token_validator(token) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token")
    
    all_products = local_session.query(Products).all()

    return all_products

#####################################################################
#####################################################################

@app_read.get(
    path="/all-receptions",
    summary="ONLY CLERK ACCESS: This endpoint lets us see all the receptions.",
    tags=["Products"]
)
def all_receptions(token: str = Depends(oauth2_scheme)):
    """
    ***ALL RECEPTIONS***

    This endpoint will let any CLERK see all the reception of products recorded.

    Parameters:
    - ***token***: str - Depends

    Returns a list with all the reception of products listed.
    """
    if token_validator(token) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token")
    
    if clerk_verifier(token) == False and manager_verifier(token) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This employee is not authorized.")

    all_receptions = local_session.query(ProductsReceived).all()
    return all_receptions