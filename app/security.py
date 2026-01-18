import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import crud
from .database import get_db
from .models import User

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
DEV_MODE = os.environ.get("DEV_MODE", "false").lower() == "true"
DEV_USER_ID = os.environ.get("DEV_USER_ID", "5719256cbd6248ca9be76f1fbc7")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if DEV_MODE:
        return await get_current_user_override(db)
    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail="JWT_SECRET_KEY not set on server")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("userId") or payload.get("user_id")
        if user_id is None:
            print("ERROR: JWT payload does not contain 'userId' or 'user_id' claim.")
            raise credentials_exception
    except JWTError as e:
        print(f"ERROR: JWT validation failed. Error: {e}")
        raise credentials_exception

    user = crud.get_user(db, user_id=user_id)
    if user is None:
        print(f"ERROR: User with ID '{user_id}' from token not found in our database.")
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_user_override(db: Session = Depends(get_db)) -> User:
    """
    Bypasses authentication. ONLY active if DEV_MODE=true in .env
    """
    if not DEV_MODE:
        raise HTTPException(status_code=403, detail="Dev mode is disabled.")

    user = crud.get_user(db, user_id=DEV_USER_ID)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dev user '{DEV_USER_ID}' not found in DB."
        )
    return user