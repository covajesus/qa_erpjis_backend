from fastapi import APIRouter, Depends
from app.backend.db.database import get_db
from sqlalchemy.orm import Session
from app.backend.schemas import UserLogin, SalarySettlement
from app.backend.classes.salary_settlement_class import SalarySettlementClass
from app.backend.classes.document_employee_class import DocumentEmployeeClass
from app.backend.auth.auth_user import get_current_active_user
from fastapi import UploadFile, File
import os
from app.backend.classes.dropbox_class import DropboxClass
from typing import List

salary_settlements = APIRouter(
    prefix="/salary_settlements",
    tags=["SalarySettlements"]
)

@salary_settlements.get("/")
def index(session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    data = SalarySettlementClass(db).get_all()

    return {"message": data}

@salary_settlements.get("/all/{page}")
def all(page:int = None, session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    data = SalarySettlementClass(db).get_all_with_pagination(page, 10)

    return {"message": data}

@salary_settlements.get("/edit/{rut}/{page}")
def edit(rut:int, page:int = None, session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    data = SalarySettlementClass(db).get("rut", rut, 2, page)

    return {"message": data}

@salary_settlements.get("/download/{id}")
def download(id:int, session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    data = SalarySettlementClass(db).download(id)

    return {"message": data}

@salary_settlements.post("/store")
def store(form_data: SalarySettlement = Depends(SalarySettlement.as_form), support: UploadFile = File(...), session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    dropbox_client = DropboxClass(db)

    filename = dropbox_client.upload(name=str(form_data.rut), description='liquidacion', data=support,
                                 dropbox_path='/salary_settlements/', computer_path=os.path.join(os.path.dirname(__file__)))

    data = SalarySettlementClass(db).store(form_data, filename)

    return {"message": data}

@salary_settlements.post("/multiple_store")
def multiple_store(files: List[UploadFile] = File(...), session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    dropbox_client = DropboxClass(db)

    for file in files:
        file_detail = file.filename.split('_')

        form_data = {}
        form_data['rut'] = file_detail[3]

        filename = dropbox_client.upload(name=str(form_data['rut']), description='liquidacion', data=file,
                                 dropbox_path='/salary_settlements/', computer_path=os.path.join(os.path.dirname(__file__)))

        data = SalarySettlementClass(db).store_multiple(form_data, filename)

    return {"message": 1}


@salary_settlements.delete("/delete/{id}")
def delete(id:int, session_user: UserLogin = Depends(get_current_active_user), db: Session = Depends(get_db)):
    document_employee = DocumentEmployeeClass(db).get("id", id)
    data = SalarySettlementClass(db).delete_salary_settlement(id)

    if data == 1 :
        if document_employee.support != '' and document_employee.support != None:
            response = DropboxClass(db).delete('/salary_settlements/', document_employee.support)
          
        if response == 1:
            data = 1
        else:
            data = 0
    else:
        data = 0  
    return {"message": data}