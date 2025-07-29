# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class CalculationBase(BaseModel):
    expression: str
    result: str

class CalculationCreate(CalculationBase):
    pass

class CalculationRead(CalculationBase):
    id: int

    class Config:
        orm_mode = True
