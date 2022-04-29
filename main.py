# In this module we will load all of the endpoints.

from fastapi import FastAPI
from routes.create import app_create
from routes.read import app_read
from routes.delete import app_delete
from security.jwt_handler import app_security

app = FastAPI()


@app.get(path="/", summary="This endpoint just intends to welcome users.", tags=["Welcome"])
def welcome_message():
    return {"message": "Welcome y'all to check out my Inventory Managment API."}

app.include_router(app_create)
app.include_router(app_read)
app.include_router(app_security)
app.include_router(app_delete)
