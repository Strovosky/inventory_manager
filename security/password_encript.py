# In this module will create the functions to hash and validate the passwords.

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# This function hashes the password.
def password_hasher(passw):
    hashed_passw = pwd_context.encrypt(passw)
    return hashed_passw

# This function makes sure the hashed password and the string password are the same.
def password_validator(hashed_passw, passw):
    if not pwd_context.verify(hashed_passw, passw):
        return False
    return True