from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from app.auth import get_password_hash, create_access_token, verify_password, get_current_user
router=APIRouter()
@router.post("/signup", response_model=UserResponse)
def signup(
    user: UserCreate,
    db: Session=Depends(get_db)
):
    existing_user=db.query(User).filter(User.email==user.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account"
        )
        
    hashed_password=get_password_hash(user.password)
    new_user=User(
        email=user.email,
        hashed_password=hashed_password
        )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
    
@router.post("/login",response_model=TokenResponse)
def login(
    user:UserLogin,
    db:Session=Depends(get_db)
):
    existing_user=db.query(User).filter(User.email==user.email).first()
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    valid_password=verify_password(
        user.password,
        existing_user.hashed_password)     
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    payload={"sub":str(existing_user.id)}
    access_token=create_access_token(payload)
    
    return {
        "access_token":access_token,
        "token_type": "bearer"
        }
    
@router.get("/me",response_model=UserResponse)
def me(
    current_user:User=Depends(get_current_user)
):
   return current_user 