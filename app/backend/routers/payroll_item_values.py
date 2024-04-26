from fastapi import APIRouter, Depends
from app.backend.db.database import get_db
from sqlalchemy.orm import Session
from app.backend.schemas import UserLogin
from app.backend.classes.payroll_item_value_class import PayrollItemValueClass
from app.backend.auth.auth_user import get_current_active_user

payroll_item_values = APIRouter(
    prefix="/payroll_item_values",
    tags=["PayrollItemValues"]
)

@payroll_item_values.get("/{item_id}/{period}")
def index(item_id:int, period:str, session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    data = PayrollItemValueClass(db).get_all(item_id, period)

    return {"message": data}