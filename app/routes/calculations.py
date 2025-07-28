# app/router/calculations.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database

router = APIRouter(
    prefix="/calculations",
    tags=["calculations"]
)

# Create (Add)
@router.post("/", response_model=schemas.CalculationRead)
def create_calculation(request: schemas.CalculationCreate, db: Session = Depends(database.get_db)):
    new_calc = models.Calculation(**request.dict())
    db.add(new_calc)
    db.commit()
    db.refresh(new_calc)
    return new_calc

# Browse (GET all)
@router.get("/", response_model=list[schemas.CalculationRead])
def get_all_calculations(db: Session = Depends(database.get_db)):
    return db.query(models.Calculation).all()

# Read (GET by ID)
@router.get("/{id}", response_model=schemas.CalculationRead)
def get_calculation(id: int, db: Session = Depends(database.get_db)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc

# Edit (PUT)
@router.put("/{id}", response_model=schemas.CalculationRead)
def update_calculation(id: int, request: schemas.CalculationCreate, db: Session = Depends(database.get_db)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    for key, value in request.dict().items():
        setattr(calc, key, value)
    db.commit()
    db.refresh(calc)
    return calc

# Delete
@router.delete("/{id}")
def delete_calculation(id: int, db: Session = Depends(database.get_db)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calc)
    db.commit()
    return {"detail": "Calculation deleted successfully"}
