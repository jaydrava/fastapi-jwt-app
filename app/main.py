from fastapi import FastAPI, Form, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
import ast
import operator
from typing import Optional
from app.routes import users, calculations
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.security import verify_password

app = FastAPI()
app.include_router(users.router)
app.include_router(calculations.router)

# In-memory user storage
users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- User Auth Endpoints ---

@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": ""})

@app.post("/register", response_class=HTMLResponse)
async def post_register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"[Register Attempt] Email received: {email}")

    # Check if email already exists in DB
    existing_email = db.query(models.User).filter(models.User.email == email).first()
    if existing_email:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Email already registered"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Validate password length
    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Password must be at least 6 characters"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Create new user
    hashed_password = security.hash_password(password)
    new_user = models.User(username=email.split('@')[0], email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"User registered: {email}")

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "message": "Registration successful"},
        status_code=status.HTTP_200_OK,
    )

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})

@app.post("/login", response_class=HTMLResponse)
async def post_login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"Login attempt email: {email}")

    # Query user from DB by email
    user = db.query(models.User).filter(models.User.email == email).first()
    print(f"User found in DB: {user}")

    if user:
        print(f"Stored hashed password: {user.hashed_password}")
        is_valid = security.verify_password(password, user.hashed_password)
        print(f"Password verification result: {is_valid}")
    else:
        is_valid = False

    if user and is_valid:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Login successful"},
            status_code=200,
        )
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Invalid credentials"},
            status_code=401,
        )
# --- Calculation storage and logic ---

calculations_db = []
next_id = 1

def safe_eval(expr: str):
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Num):  # Python <3.8
            return node.n
        elif isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Unsupported constant type")
        elif isinstance(node, ast.BinOp):
            op_func = allowed_operators.get(type(node.op))
            if op_func is None:
                raise ValueError("Unsupported operator")
            return op_func(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op_func = allowed_operators.get(type(node.op))
            if op_func is None:
                raise ValueError("Unsupported unary operator")
            return op_func(_eval(node.operand))
        else:
            raise ValueError("Unsupported expression")

    node = ast.parse(expr, mode='eval')
    return _eval(node.body)

# --- Calculation Endpoints ---

@app.get("/calculations")
async def browse_calculations():
    return calculations_db

@app.get("/calculations/{calc_id}")
async def read_calculation(calc_id: int):
    for calc in calculations_db:
        if calc["id"] == calc_id:
            return calc
    raise HTTPException(status_code=404, detail="Calculation not found")

@app.post("/calculations")
async def add_calculation(expression: str = Form(...)):
    global next_id
    try:
        result = safe_eval(expression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {e}")

    calc = {"id": next_id, "expression": expression, "result": result}
    calculations_db.append(calc)
    next_id += 1
    return calc

@app.put("/calculations/{calc_id}")
async def edit_calculation(calc_id: int, expression: str = Form(...)):
    for calc in calculations_db:
        if calc["id"] == calc_id:
            try:
                result = safe_eval(expression)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid expression: {e}")
            calc["expression"] = expression
            calc["result"] = result
            return calc
    raise HTTPException(status_code=404, detail="Calculation not found")

@app.delete("/calculations/{calc_id}")
async def delete_calculation(calc_id: int):
    for i, calc in enumerate(calculations_db):
        if calc["id"] == calc_id:
            calculations_db.pop(i)
            return {"detail": f"Calculation {calc_id} deleted"}
    raise HTTPException(status_code=404, detail="Calculation not found")
