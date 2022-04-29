# In this module, we'll authenticate the employees using utility functions and
# using jwt we'll create the token.


from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.db_models import local_session, Employees
from models.pydantic_models import Positions, FullEmployee
from security.password_encript import password_validator

from decouple import config
from datetime import datetime, timedelta

from jose import jwt, JWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token_url")

app_security = APIRouter()

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 20

authorized_position_manager = Positions.Manager
authorized_position_clerk = Positions.Clerk
authorized_position_cashier = Positions.Cashier


# This utility function will verify that the username and passwords are correct.
def employee_validator(emp_username, emp_passw):
    all_employees = local_session.query(Employees).all()
    
    for employee in all_employees:
        if employee.username == emp_username and password_validator(emp_passw, employee.password) != False:
            return employee
    return False



def expire_time_setter():
    expiring_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return expiring_time


# This utility function will create the token taking the "sub" (data), the "exp", secret_key and algorithm.
def token_writer(data: dict):
    token = jwt.encode(claims={**data, "exp": expire_time_setter()}, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def token_validator(token):
    try:
        jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return False


def no_duplicate_employee_verifier(employee: FullEmployee):
    all_employees: Employees = local_session.query(Employees).all()
    
    for current_employee in all_employees:
        if current_employee.cellphone == employee.cellphone or current_employee.username == employee.username or current_employee.email ==employee.email:
            return False
    return True


# Let's verify if the logged in employee is a manager.
# Otherwise, they shouldn't be able to create new employees.
def manager_verifier(token):
    decoded_token = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])

    employee_id = decoded_token["sub"]

    current_employee = local_session.query(Employees).filter(Employees.employee_id == employee_id).first()

    if current_employee.position != authorized_position_manager.value:
        return False
    return True


def clerk_verifier(token):
    decoded_token = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])

    employee_id = decoded_token["sub"]

    current_employee = local_session.query(Employees).filter(Employees.employee_id == employee_id).first()

    if current_employee.position != authorized_position_clerk.value:
        return False
    return True


def cashier_verifier(token):
    decoded_token = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])

    employee_id = decoded_token["sub"]

    current_employee = local_session.query(Employees).filter(Employees.employee_id == employee_id).first()

    if current_employee.position != authorized_position_cashier.value:
        return False
    return True


@app_security.post(
    path="/token_url",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Here we'll authenticate the employees.",
    tags=["Security"])
def employee_autheticator(form_data: OAuth2PasswordRequestForm = Depends()):
    
    employee = employee_validator(form_data.username, form_data.password)

    if employee == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "incorrect username or password."})

    employee_id = str(employee.employee_id)

    access_token = token_writer({"sub": employee_id})
    return {"access_token": access_token, "token_type": "bearer"}
