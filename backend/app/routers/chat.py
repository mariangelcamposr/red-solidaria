from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/matches/{match_id}/messages',tags=['Chat'])
def authorized(match_id,user,db):
    m=db.query(models.Match).filter(models.Match.id==match_id).first()
    if not m: raise HTTPException(404,'Coincidencia no encontrada')
    d=db.query(models.Donation).filter(models.Donation.id==m.donation_id).first()
    if user.id not in (m.requester_id,d.donor_id): raise HTTPException(403,'No participás de esta conversación')
    return m,d
@router.post('',response_model=schemas.MessageOut,status_code=201)
def send(match_id:int,payload:schemas.MessageCreate,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    m,d=authorized(match_id,user,db); m.status=models.MatchStatus.COORDINATING; msg=models.Message(match_id=match_id,sender_id=user.id,content=payload.content); db.add(msg); other=d.donor_id if user.id==m.requester_id else m.requester_id; db.add(models.Notification(user_id=other,kind='message',title='Nuevo mensaje',message=f'Tenés un nuevo mensaje sobre la coincidencia #{match_id}.')); db.commit(); db.refresh(msg); return msg
@router.get('',response_model=list[schemas.MessageOut])
def list_messages(match_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    authorized(match_id,user,db); return db.query(models.Message).filter(models.Message.match_id==match_id).order_by(models.Message.created_at.asc()).all()
