from typing import Optional
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from .. import auth,models
from ..database import get_db
from ..services.matching import distance_km
router=APIRouter(prefix='/search',tags=['Búsqueda'])
@router.get('/donations')
def search(resource_type:Optional[str]=None,category:Optional[str]=None,location:Optional[str]=None,max_distance_km:Optional[float]=Query(None,ge=0),status:Optional[str]=None,urgent:Optional[bool]=None,sort_by:str='relevance',db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    q=db.query(models.Donation).filter(models.Donation.status.in_([models.DonationStatus.VISIBLE,models.DonationStatus.MATCHED]))
    if resource_type:q=q.filter(models.Donation.resource_type.ilike(f'%{resource_type}%'))
    if category:q=q.filter(models.Donation.category.ilike(f'%{category}%'))
    if location:q=q.filter(models.Donation.location.ilike(f'%{location}%'))
    if status:
        try:q=q.filter(models.Donation.status==models.DonationStatus(status))
        except ValueError:pass
    if urgent is not None:q=q.filter(models.Donation.is_urgent==urgent)
    rows=q.all()
    if max_distance_km is not None and user.latitude is not None and user.longitude is not None: rows=[d for d in rows if distance_km(user.latitude,user.longitude,d.latitude,d.longitude) is not None and distance_km(user.latitude,user.longitude,d.latitude,d.longitude)<=max_distance_km]
    if sort_by=='distance' and user.latitude is not None and user.longitude is not None: rows.sort(key=lambda d:distance_km(user.latitude,user.longitude,d.latitude,d.longitude) if distance_km(user.latitude,user.longitude,d.latitude,d.longitude) is not None else 999999)
    elif sort_by=='expiry': rows.sort(key=lambda d:d.expiry_date or __import__('datetime').datetime.max)
    elif sort_by=='date': rows.sort(key=lambda d:d.created_at,reverse=True)
    elif sort_by=='quantity': rows.sort(key=lambda d:d.quantity,reverse=True)
    return rows
