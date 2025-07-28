# app/schemas/user.py
from pydantic import BaseModel, EmailStr

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

class CalculationBase(BaseModel):
    expression: str
    result: str

class CalculationCreate(CalculationBase):
    pass

class CalculationRead(CalculationBase):
    id: int

    class Config:
        orm_mode = True
