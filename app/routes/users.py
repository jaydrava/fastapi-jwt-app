# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
from app import models, schemas, database, security

router = APIRouter(prefix="/users", tags=["Users"])


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# JSON: Register endpoint
# -----------------------------
@router.post("/register", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check username duplicate
    existing_username = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check email duplicate
    existing_email = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = security.hash_password(user.password)
    new_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -----------------------------
# JSON: Login endpoint
# -----------------------------
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if not db_user or not security.verify_password(
        user.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = security.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


# -----------------------------
# HTML Form: Register endpoint
# -----------------------------
@router.post("/register_form")
def register_user_form(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Check username duplicate
    existing_username = (
        db.query(models.User).filter(models.User.username == username).first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check email duplicate
    existing_email = db.query(models.User).filter(models.User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = security.hash_password(password)
    new_user = models.User(username=username, email=email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)


# -----------------------------
# HTML Form: Login endpoint
# -----------------------------
@router.post("/login_form")
def login_user_form(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user or not security.verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Redirect to home or dashboard after login
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
