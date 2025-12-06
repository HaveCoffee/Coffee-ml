import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud
from .database import get_db
from .models import User

# --- Configuration ---
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM")
DEV_USER_ID = "5719256c-bd62-48ca-9be7-76f1fbc7"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # tokenUrl is a dummy path, not used

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    A dependency that validates a JWT and returns the corresponding User object from the database.
    This function will be injected into protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_override(db: Session = Depends(get_db)) -> User:
    """
    A dependency override for development. Bypasses JWT validation and returns
    a hardcoded user from the database.
    
    ONLY USE THIS WHEN THE AUTH SERVICE IS DOWN.
    """
    print("--- WARNING: JWT AUTHENTICATION IS BYPASSED ---")
    user = crud.get_user(db, user_id=DEV_USER_ID)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dev mode user with ID '{DEV_USER_ID}' not found in the database. "
                   "Please update DEV_USER_ID in security.py or seed the database."
        )
    return user