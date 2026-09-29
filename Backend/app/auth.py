from pwdlib import PasswordHash
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta
from jose import jwt,JWTError
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session
password_hasher=PasswordHash.recommended()

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def get_password_hash(password:str)->str:
    return password_hasher.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return password_hasher.verify(plain_password,hashed_password)

def create_access_token(data:dict)->str:
    to_encode=data.copy()
    expire= datetime.now()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"]=expire
    jwt_token=jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return jwt_token

def verify_access_token(token:str)->int:
    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id=payload.get("sub")
        if not isinstance(user_id,str) or not user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user_id=int(user_id)
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

bearer_scheme=HTTPBearer()

def get_current_user(
    credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme),
    db:Session=Depends(get_db)
):
    token=credentials.credentials
    user_id=verify_access_token(token)
    user=db.query(User).filter(User.id==user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return user