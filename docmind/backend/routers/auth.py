from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from services.auth import verify_password, get_password_hash, create_access_token
from db.database import users_collection

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    email: str

@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = {
        "email": user.email,
        "hashed_password": hashed_password
    }
    await users_collection.insert_one(new_user)
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "email": user.email}

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "email": user.email}
