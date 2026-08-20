from datetime import datetime,timedelta
from sqlalchemy import func
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/dashboard',tags=['Dashboard'])
@router.get('',response_model=schemas.DashboardOut)
def dashboard(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    donations=db.query(models.Donation).filter(models.Donation.donor_id==user.id).all(); reqs=db.query(models.Request).filter(models.Request.requester_id==user.id).all(); txs=db.query(models.Transaction).filter((models.Transaction.donor_id==user.id)|(models.Transaction.requester_id==user.id)).all(); matches=db.query(models.Match).filter(models.Match.requester_id==user.id,models.Match.status!=models.MatchStatus.CLOSED).count()
    by={}
    for d in donations: by[d.category]=by.get(d.category,0)+1
    successful=sum(1 for t in txs if t.status==models.TransactionStatus.COMPLETED); attended=sum(1 for r in reqs if r.status==models.RequestStatus.CLOSED)
    exp=sum(1 for d in donations if d.expiry_date and datetime.utcnow()<=d.expiry_date<=datetime.utcnow()+timedelta(days=14) and d.status not in (models.DonationStatus.COMPLETED,models.DonationStatus.CANCELLED))
    return schemas.DashboardOut(active_donations=sum(d.status in (models.DonationStatus.VISIBLE,models.DonationStatus.MATCHED,models.DonationStatus.RESERVED) for d in donations),open_requests=sum(r.status==models.RequestStatus.OPEN for r in reqs),recommended_matches=matches,recent_transactions=len(txs),reputation_score=user.reputation_score,ratings_count=user.ratings_count,donations_by_category=by,requests_attended=attended,successful_rate=round(successful/len(txs)*100,1) if txs else 0,expiring_soon=exp)
