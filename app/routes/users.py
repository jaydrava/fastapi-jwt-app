from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import models, schemas, database, security

router = APIRouter(prefix="/users", tags=["Users"])  # This must be before route decorators

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register_form")
def register_user_form(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Password length validation
    if len(password) < 6:
        return JSONResponse(content={"message": "Password must be at least 6 characters"}, status_code=400)

    # Username duplicate check
    existing_username = db.query(models.User).filter(models.User.username == username).first()
    if existing_username:
        return JSONResponse(content={"message": "Username already exists"}, status_code=400)

    # Email duplicate check
    existing_email = db.query(models.User).filter(models.User.email == email).first()
    if existing_email:
        return JSONResponse(content={"message": "Email already registered"}, status_code=400)

    # Hash password and create user
    hashed = security.hash_password(password)
    new_user = models.User(username=username, email=email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return JSONResponse(content={"message": "Registration successful!"}, status_code=200)

@router.post("/login_form")
def login_user_form(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user or not security.verify_password(password, db_user.hashed_password):
        return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)

    return JSONResponse(content={"message": "Login successful!"}, status_code=200)
