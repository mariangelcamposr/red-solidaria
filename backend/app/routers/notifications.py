import json
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
from ..services.notifications import scan_expiry
router=APIRouter(prefix='/notifications',tags=['Notificaciones'])
@router.get('',response_model=list[schemas.NotificationOut])
def mine(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    scan_expiry(db); return db.query(models.Notification).filter(models.Notification.user_id==user.id).order_by(models.Notification.created_at.desc()).limit(100).all()
@router.patch('/{notification_id}/read',response_model=schemas.NotificationOut)
def mark_read(notification_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    n=db.query(models.Notification).filter(models.Notification.id==notification_id,models.Notification.user_id==user.id).first()
    if not n: raise HTTPException(404,'Notificación no encontrada')
    n.read=True; db.commit(); db.refresh(n); return n
@router.post('/search-favorites',response_model=schemas.SearchFavoriteOut)
def save_search(payload:schemas.SearchFavoriteCreate,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    row=models.SearchFavorite(user_id=user.id,name=payload.name,filters_json=json.dumps(payload.filters.model_dump(),ensure_ascii=False),alerts_enabled=payload.alerts_enabled); db.add(row); db.commit(); db.refresh(row); return {'id':row.id,'name':row.name,'filters':json.loads(row.filters_json),'alerts_enabled':row.alerts_enabled,'created_at':row.created_at}
@router.get('/search-favorites',response_model=list[schemas.SearchFavoriteOut])
def searches(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    rows=db.query(models.SearchFavorite).filter(models.SearchFavorite.user_id==user.id).all(); return [{'id':r.id,'name':r.name,'filters':json.loads(r.filters_json),'alerts_enabled':r.alerts_enabled,'created_at':r.created_at} for r in rows]
