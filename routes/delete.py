# This module will be in charge of deleting users as well as products.

from fastapi import APIRouter, status, HTTPException, Depends
from schemas.db_models import local_session
from security.jwt_handler import oauth2_scheme, token_validator, manager_verifier
from schemas.db_models import Employees

app_delete = APIRouter()


@app_delete.delete(
    path="/delete-user",
    summary="ONLY MANAGER ACCESS: This endpoint will be in charge of deleting users.",
    tags=["Employees"])
def delete_user(employee_to_delete_id: int, token: str = Depends(oauth2_scheme)):
    """
    ***DELETE USER***

    This endpoint will let any MANAGER delete any user.

    Parameters:
    - ***employee_to_delete_id***: int
    - ***token***: str - Depends

    Returns a dictionary with info about the employee deleted.
    """
    if token_validator(token) == False:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "invalid or expired token"})

    # Only the clerk can add new products.
    if not manager_verifier(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Employee not authorized to delete employees."})
    
    user_to_delete = local_session.query(Employees).filter(Employees.employee_id == employee_to_delete_id).first()

    local_session.delete(user_to_delete)
    local_session.commit()

    return {"Status": f"Employee {employee_to_delete_id} deleted"}
