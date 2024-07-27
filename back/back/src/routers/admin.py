from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from schema import admin as admin_schema
import database
from fastapi.security import OAuth2PasswordRequestForm
from utils.crypt import create_access_token
from utils.logger import logger
router = APIRouter()

# @router.post("/login/", response_model=admin_schema.Admin)
# def login(admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # return admin_cud.login(db=db, admin=admin_schema.AdminLogin(username=admin.username, password=admin.password))

@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    admin = admin_cud.authenticate_user(db, form_data.username, form_data.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        subject=admin.username
    )
    return {"access_token": access_token, "token_type": "bearer"}