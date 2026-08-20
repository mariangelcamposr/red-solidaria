from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
from ..services.ai import assistant_answer
router=APIRouter(prefix='/assistant',tags=['Asistente inteligente'])
@router.post('/message',response_model=schemas.AssistantMessageOut)
def message(payload:schemas.AssistantRequest,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    db.add(models.AssistantMessage(user_id=user.id,sender='user',content=payload.message)); answer=assistant_answer(payload.message); row=models.AssistantMessage(user_id=user.id,sender='assistant',content=answer); db.add(row); db.commit(); db.refresh(row); return row
@router.get('/history',response_model=list[schemas.AssistantMessageOut])
def history(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    return db.query(models.AssistantMessage).filter(models.AssistantMessage.user_id==user.id).order_by(models.AssistantMessage.created_at.asc()).all()
