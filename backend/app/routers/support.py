from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/support',tags=['Soporte'])
@router.post('',response_model=schemas.SupportOut,status_code=201)
def create(payload:schemas.SupportCreate,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    row=models.SupportRequest(user_id=user.id,subject=payload.subject,message=payload.message); db.add(row); db.commit(); db.refresh(row); return row
@router.get('',response_model=list[schemas.SupportOut])
def mine(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)): return db.query(models.SupportRequest).filter(models.SupportRequest.user_id==user.id).order_by(models.SupportRequest.created_at.desc()).all()
