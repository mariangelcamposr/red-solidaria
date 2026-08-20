from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/transactions',tags=['Transacciones'])
def pair(match_id,db):
    m=db.query(models.Match).filter(models.Match.id==match_id).first()
    if not m: raise HTTPException(404,'Coincidencia no encontrada')
    d=db.query(models.Donation).filter(models.Donation.id==m.donation_id).first(); return m,d
@router.post('/{match_id}/coordinate',response_model=schemas.TransactionOut)
def coordinate(match_id:int,payload:schemas.TransactionCoordinate,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    m,d=pair(match_id,db)
    if user.id not in (m.requester_id,d.donor_id): raise HTTPException(403,'No participás de esta coordinación')
    tx=db.query(models.Transaction).filter(models.Transaction.match_id==match_id).first()
    if not tx: tx=models.Transaction(match_id=match_id,donation_id=d.id,donor_id=d.donor_id,requester_id=m.requester_id); db.add(tx)
    if d.status in (models.DonationStatus.COMPLETED,models.DonationStatus.CANCELLED,models.DonationStatus.EXPIRED): raise HTTPException(400,'La donación no está disponible')
    d.status=models.DonationStatus.RESERVED; m.status=models.MatchStatus.COORDINATING; tx.delivery_details=payload.delivery_details; db.commit(); db.refresh(tx); return tx
@router.post('/{match_id}/deliver',response_model=schemas.TransactionOut)
def deliver(match_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    m,d=pair(match_id,db)
    if user.id not in (m.requester_id,d.donor_id): raise HTTPException(403,'No participás de esta entrega')
    tx=db.query(models.Transaction).filter(models.Transaction.match_id==match_id).first()
    if not tx: raise HTTPException(400,'Primero coordiná la entrega')
    if d.status==models.DonationStatus.COMPLETED: raise HTTPException(400,'La donación ya fue entregada')
    m.status=models.MatchStatus.DELIVERED; tx.status=models.TransactionStatus.PENDING_CONFIRMATION; db.commit(); db.refresh(tx); return tx
@router.post('/{transaction_id}/confirm',response_model=schemas.TransactionOut)
def confirm(transaction_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    tx=db.query(models.Transaction).filter(models.Transaction.id==transaction_id).first()
    if not tx: raise HTTPException(404,'Transacción no encontrada')
    if user.id==tx.donor_id: tx.donor_confirmed=True
    elif user.id==tx.requester_id: tx.requester_confirmed=True
    else: raise HTTPException(403,'No participás de esta transacción')
    if tx.donor_confirmed and tx.requester_confirmed:
        tx.status=models.TransactionStatus.COMPLETED; tx.completed_at=datetime.utcnow(); d=db.query(models.Donation).filter(models.Donation.id==tx.donation_id).first(); d.status=models.DonationStatus.COMPLETED; m=db.query(models.Match).filter(models.Match.id==tx.match_id).first(); m.status=models.MatchStatus.CLOSED; r=db.query(models.Request).filter(models.Request.id==m.request_id).first(); r.status=models.RequestStatus.CLOSED; db.add(models.Notification(user_id=tx.donor_id,kind='delivery',title='Entrega confirmada',message=f'La transacción #{tx.id} fue completada.')); db.add(models.Notification(user_id=tx.requester_id,kind='delivery',title='Entrega confirmada',message=f'La transacción #{tx.id} fue completada.'))
    db.commit(); db.refresh(tx); return tx
@router.get('/me',response_model=list[schemas.TransactionOut])
def mine(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    return db.query(models.Transaction).filter((models.Transaction.donor_id==user.id)|(models.Transaction.requester_id==user.id)).order_by(models.Transaction.created_at.desc()).all()
