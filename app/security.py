import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud
from .database import get_db
from .models import SharedUser, AppUser


SECRET_KEY = os.environ.get("JWT_SECRET")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
DEV_USER_ID = os.environ.get("DEV_USER_ID")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> SharedUser:
    """
    The production security dependency. It validates a real JWT and provisions an AppUser.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail="JWT_SECRET not set on server")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("userId") or payload.get("user_id")
        if user_id is None:
            print("ERROR: JWT payload does not contain 'userId' or 'user_id' claim.")
            raise credentials_exception
    except JWTError as e:
        print(f"ERROR: JWT validation failed. Error: {e}")
        raise credentials_exception

    user = db.query(SharedUser).filter(SharedUser.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found in main directory")

    app_user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not app_user:
        print(f"First-time interaction for user {user.user_id}. Provisioning AppUser record...")
        new_app_user = AppUser(user_id=user.user_id)
        db.add(new_app_user)
        db.commit()
        print("   -> AppUser record created.")
    
    return user

async def get_current_user_override(db: Session = Depends(get_db)) -> SharedUser:
    """
    A dependency override for development. Bypasses JWT validation and returns
    a hardcoded user from the database. ONLY active if DEV_MODE=true.
    """
    if not DEV_USER_ID:
        raise HTTPException(status_code=500, detail="DEV_USER_ID not set in .env for dev mode.")

    user = db.query(SharedUser).filter(SharedUser.user_id == DEV_USER_ID).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dev mode user with ID '{DEV_USER_ID}' not found in the shared 'users' table."
        )
    return user