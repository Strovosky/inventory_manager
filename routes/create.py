# In this module we'll create the crud endpoints for the employees and the products.

from fastapi import APIRouter, status, Depends, Body, HTTPException
from schemas.db_models import ProductsSold, local_session
from security.jwt_handler import oauth2_scheme, no_duplicate_employee_verifier, token_validator, manager_verifier, clerk_verifier, cashier_verifier
from models.pydantic_models import FullEmployee, BaseProduct, Reception, Sale, Spoiled, Returned
from schemas.db_models import Employees, Products, ProductsReceived, ReturnedProducts
from security.password_encript import password_hasher


app_create = APIRouter()


@app_create.post(
    path="/new_employee",
    status_code=status.HTTP_201_CREATED,
    summary="ONLY MANAGER ACCESS: Here you can create the new employees.",
    tags=["Employees"])
def new_employee(
    new_employee: FullEmployee = Body(...),
    token: str = Depends(oauth2_scheme)):
    
    """
    ***NEW EMPLOYEE***

    This endpoint will let any manager create a new employee.

    Parameters:
    - ***new_employee***: FullEmployee - Body.
    - ***token***: str - Depends

    Returns a dictionary stating that a new employee was created.
    """

    if token_validator(token) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid or expired token"})
    
    # Only the manager can add new employees.
    if not manager_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to create new employees."})
    
    if no_duplicate_employee_verifier(new_employee) == False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"error": "This info already belongs to another employee."}
        )
    
    new_db_employee = Employees(
        first_name = new_employee.first_name.title(),
        last_name = new_employee.last_name.title(),
        username = new_employee.username,
        cellphone = new_employee.cellphone,
        email = new_employee.email,
        position = new_employee.position.value,
        password = password_hasher(new_employee.password)
    )

    local_session.add(new_db_employee)
    local_session.commit()

    return {"Status": "New Employee Created"}


@app_create.post(
    path="/new-product",
    status_code=status.HTTP_201_CREATED,
    summary="ONLY MANAGER ACCESS: Here you'll be able to create a new product.",
    response_model=BaseProduct,
    tags=["Products"])
def new_product(new_product: BaseProduct, token: str = Depends(oauth2_scheme)):
    """
    ***NEW PRODUCT***

    This endpoint will let any MANAGER create a new product to manage in the system.

    Parameters:
    - ***new_product***: BaseProduct - pydantic model.
    - ***token***: str - Depends

    Returns the pydantic model with the info of the new product created.
    """
    
    if token_validator(token) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid or expired token"})
    
    # Only the manager can add new employees.
    if not manager_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to create new employees."})

    new_product_db = Products(
        product_name = new_product.name,
        description = new_product.description,
        brand = new_product.brand,
        category = new_product.category.value,
        purchase_price = new_product.purchase_prise,
        sale_price = new_product.sale_price
    )

    local_session.add(new_product_db)
    local_session.commit()

    return new_product

##############################################################################
##############################################################################

@app_create.post(
    path="/new_reception",
    status_code=status.HTTP_201_CREATED,
    summary="ONLY CLERK ACCESS: This endpoin will let the clerk report when a product is received in the warehouse.",
    tags=["Products"],
    response_model=Reception)
def new_reception(new_reception: Reception, token: str = Depends(oauth2_scheme)):
    """
    ***NEW RECEPTION***

    This endpoint will let any Clerk regirster any product they receive in the warehouse.

    Parameters:
    - ***new_reception***: BaseProduct - pydantic model.
    - ***token***: str - Depends

    Returns a pydantic model with info of the reception.
    """
    if token_validator(token) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid or expired token"})
    
    # Only the clerk can add new products.
    if not clerk_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to create new receptions."})
    
    product = local_session.query(Products).filter(Products.product_id == new_reception.product_id).first()

    if product == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":f"Product {new_reception.product_id} not found."})

    new_reception_db = ProductsReceived(
        product_id = new_reception.product_id,
        quantity = new_reception.quantity
    )

    product.quantity_in_stock += new_reception.quantity

    local_session.add(new_reception_db)
    local_session.commit()

    return new_reception

##############################################################################
##############################################################################

@app_create.post(
    path="/new_sale",
    summary="ONLY CASHIER ACCESS: This endpoint will create a new product sale.",
    tags=["Products"]
)
def new_sale(new_sale: Sale, token: str = Depends(oauth2_scheme)):
    """
    ***NEW SALE***

    This endpoint will let any CLERK register the sale of a product.
    By doing so, the variable ***quantity_sold* of the product in the database will be automatically updated.

    Parameters:
    - ***new_sale***: Sale - pydantic model.
    - ***token***: str - Depends

    Returns a dictionary with info of the sale.
    """
    
    if token_validator(token) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid or expired token"})
    
    # Only the clerk can add new products.
    if not cashier_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to perfome a sale."})    
    
    new_sale_db = ProductsSold(
        product_id = new_sale.product_id,
        quantity = new_sale.quantity,
        note = new_sale.note
    )
    local_session.add(new_sale_db)
    local_session.commit()

    product = local_session.query(Products).filter(Products.product_id == new_sale.product_id).first()

    if product == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":f"Product {new_reception.product_id} not found."})

    product.quantity_sold += new_sale_db.quantity
    product.quantity_in_stock -= new_sale.quantity

    return {"Receipt": f"Product {product.product_name} with number of sale {new_sale_db.sale_number}"}

##############################################################################
##############################################################################

@app_create.post(
    path="/spoiled-products",
    summary="ONLY CLERK ACCESS: This endpoint will register any spoiled or damaged products.",
    tags=["Products"]
)
def spoiled_product(new_spoiled_product: Spoiled, token: str = Depends(oauth2_scheme)):
    """
    ***SPOILED PRODUCT***

    This endpoint will let any CLERK report whenever he spots spoiled or damaged products.
    By doing so, the variables ***quantity_spoiled*** and ***quantity_in_stock*** will be updated.

    Parameters:
    - ***new_spoiled_product***: BaseProduct - pydantic model.
    - ***token***: str - Depends

    Returns a dictionary with a report of how many products were spoiled.
    """
    
    if not token_validator(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid or expired token"})
    
    # Only the clerk can add new products.
    if not clerk_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to perfome a sale."})    
    
    new_spoiled_product_db = Spoiled(
        product_id = new_spoiled_product.product_id,
        quantity = new_spoiled_product.quantity,
        note = new_spoiled_product.note
    )
    local_session.add(new_spoiled_product_db)
    local_session.commit()

    product = local_session.query(Products).filter(Products.product_id == new_spoiled_product.product_id).first()

    if product == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":f"Product {new_reception.product_id} not found."})

    product.quantity_spoiled += new_spoiled_product_db.quantity
    product.quantity_in_stock -= new_spoiled_product_db.quantity

    return {"Report": f"Product {new_spoiled_product_db.product_id} had {new_spoiled_product.quantity} pieces spoiled."}

##############################################################################
##############################################################################

@app_create.post(
    path="/return-product",
    summary="ONLY CASHIER ACCESS: This endpoint will register product that is returned.",
    tags=["Products"]
)
def return_product(new_returned_product: Returned, token: str = Depends(oauth2_scheme)):
    """
    ***RETURN PRODUCT***

    This endpoint will let any CASHIER return products.
    By doing so, the variables ***quantity_in_stock*** and optionally ***quantity_spoiled*** will be updated.

    Parameters:
    - ***new_returned_product***: Returned - pydantic model.
    - ***token***: str - Depends

    Returns a dictionary with a report of how many products were returned.
    """
    if token_validator(token) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid or expired token"})
    
    # Only the clerk can add new products.
    if not cashier_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to perfome a sale."})    
    
    new_return_db = ReturnedProducts(
        product_id = new_returned_product.product_id,
        quantity = new_returned_product.quantity,
        note = new_returned_product.note
    )
    local_session.add(new_return_db)
    local_session.commit()

    product = local_session.query(Products).filter(Products.product_id == new_returned_product.product_id).first()

    if product == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":f"Product {new_reception.product_id} not found."})

    product.quantity_in_stock += new_return_db.quantity

    if new_returned_product.is_spoiled:
        product.quantity_spoiled += new_return_db.quantity
        product.quantity_in_stock -= new_return_db.quantity

    return {"Status": f"Product {product.product_name} was returned. Quantity returned: {new_returned_product.quantity}."}
