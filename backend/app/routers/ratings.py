from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/transactions/{transaction_id}/ratings',tags=['Calificaciones'])
@router.post('',response_model=schemas.RatingOut,status_code=201)
def rate(transaction_id:int,payload:schemas.RatingCreate,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    tx=db.query(models.Transaction).filter(models.Transaction.id==transaction_id).first()
    if not tx: raise HTTPException(404,'Transacción no encontrada')
    if tx.status!=models.TransactionStatus.COMPLETED: raise HTTPException(400,'La transacción debe estar completada')
    if user.id==tx.donor_id: rated=tx.requester_id
    elif user.id==tx.requester_id: rated=tx.donor_id
    else: raise HTTPException(403,'No participás de esta transacción')
    if db.query(models.Rating).filter(models.Rating.transaction_id==transaction_id,models.Rating.rater_id==user.id).first(): raise HTTPException(400,'Ya calificaste esta transacción')
    r=models.Rating(transaction_id=transaction_id,rater_id=user.id,rated_user_id=rated,score=payload.score,comment=payload.comment); db.add(r); target=db.query(models.User).filter(models.User.id==rated).first(); total=target.reputation_score*target.ratings_count+payload.score; target.ratings_count+=1; target.reputation_score=round(total/target.ratings_count,2); db.add(models.Notification(user_id=rated,kind='rating',title='Nueva calificación',message=f'Recibiste una calificación de {payload.score}/5.')); db.commit(); db.refresh(r); return r
