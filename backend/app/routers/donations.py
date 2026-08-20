import json,os,uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter,Depends,HTTPException,Query,UploadFile,File,Form,status
from sqlalchemy.orm import Session
from .. import auth,models
from ..database import get_db
from ..services import matching,ai,notifications
router=APIRouter(prefix='/donations',tags=['Donaciones'])
BASE_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../uploads'))
os.makedirs(BASE_DIR,exist_ok=True)
RESOURCE_TYPES={'medicamento','medicina','alimento','accesorio','producto de higiene','higiene','otro'}
@router.post('',status_code=201)
def create_donation(title:str=Form(...),description:str=Form(...),resource_type:str=Form(...),category:str=Form(...),quantity:float=Form(...),condition:str=Form(...),location:str=Form(...),delivery_conditions:str=Form(...),expiry_date:Optional[str]=Form(None),presentation:Optional[str]=Form(None),package_condition:Optional[str]=Form(None),latitude:Optional[float]=Form(None),longitude:Optional[float]=Form(None),is_urgent:bool=Form(False),image:UploadFile=File(...),db:Session=Depends(get_db),current_user:models.User=Depends(auth.get_current_user)):
    if quantity<=0: raise HTTPException(400,'La cantidad debe ser mayor a cero')
    if resource_type.strip().lower() not in RESOURCE_TYPES: raise HTTPException(400,'Tipo de recurso no permitido')
    exp=datetime.fromisoformat(expiry_date) if expiry_date else None
    if resource_type.lower() in ('medicamento','medicina') and (not exp or not presentation or not package_condition): raise HTTPException(400,'Los medicamentos requieren vencimiento, presentación y estado del envase')
    if resource_type.lower() in ('medicamento','medicina') and package_condition and package_condition.strip().lower() in ('abierto','abierta','sin identificación','ilegible'): raise HTTPException(400,'No se puede publicar un medicamento abierto, sin identificación o ilegible')
    if exp and exp<datetime.utcnow(): raise HTTPException(400,'No se pueden publicar productos vencidos')
    if image.content_type not in ('image/jpeg','image/png'): raise HTTPException(400,'La fotografía debe ser JPG o PNG')
    data=image.file.read()
    if len(data)>5*1024*1024: raise HTTPException(400,'La fotografía supera 5 MB')
    ext='.jpg' if image.content_type=='image/jpeg' else '.png'; filename=f'{uuid.uuid4().hex}{ext}'; path=os.path.join(BASE_DIR,filename); open(path,'wb').write(data)
    d=models.Donation(donor_id=current_user.id,title=title,description=description,resource_type=resource_type,category=category,quantity=quantity,condition=condition,location=location,latitude=latitude,longitude=longitude,expiry_date=exp,presentation=presentation,package_condition=package_condition,delivery_conditions=delivery_conditions,is_urgent=is_urgent,image_path=f'/uploads/{filename}',status=models.DonationStatus.VISIBLE)
    d.ai_analysis_result=ai.analyze_publication(title,description,resource_type,exp)
    db.add(d); db.commit(); db.refresh(d); db.add(models.Photo(donation_id=d.id,path=d.image_path,ai_result=d.ai_analysis_result)); db.commit(); db.refresh(d)
    matching.run_matching_for_donation(db,d); notifications.scan_expiry(db)
    return d
@router.get('')
def list_donations(resource_type:Optional[str]=None,category:Optional[str]=None,location:Optional[str]=None,max_distance_km:Optional[float]=Query(None,ge=0),urgent:Optional[bool]=None,mine:bool=False,sort_by:str='relevance',db:Session=Depends(get_db),current_user:models.User=Depends(auth.get_current_user)):
    notifications.scan_expiry(db); q=db.query(models.Donation)
    if mine: q=q.filter(models.Donation.donor_id==current_user.id)
    else: q=q.filter(models.Donation.status.in_([models.DonationStatus.VISIBLE,models.DonationStatus.MATCHED]))
    if resource_type:q=q.filter(models.Donation.resource_type.ilike(f'%{resource_type}%'))
    if category:q=q.filter(models.Donation.category.ilike(f'%{category}%'))
    if location:q=q.filter(models.Donation.location.ilike(f'%{location}%'))
    if urgent is not None:q=q.filter(models.Donation.is_urgent==urgent)
    items=q.all()
    if max_distance_km is not None and current_user.latitude is not None and current_user.longitude is not None:
        items=[d for d in items if matching.distance_km(current_user.latitude,current_user.longitude,d.latitude,d.longitude) is not None and matching.distance_km(current_user.latitude,current_user.longitude,d.latitude,d.longitude)<=max_distance_km]
    if sort_by=='expiry': items.sort(key=lambda d:d.expiry_date or datetime.max)
    elif sort_by=='date': items.sort(key=lambda d:d.created_at,reverse=True)
    elif sort_by=='quantity': items.sort(key=lambda d:d.quantity,reverse=True)
    else: items.sort(key=lambda d:(not d.is_urgent,d.created_at),reverse=False)
    return items
@router.get('/{donation_id}')
def get_donation(donation_id:int,db:Session=Depends(get_db)):
    d=db.query(models.Donation).filter(models.Donation.id==donation_id).first()
    if not d: raise HTTPException(404,'Donación no encontrada')
    return d
@router.get('/{donation_id}/detail')
def detail(donation_id:int,db:Session=Depends(get_db)):
    d=db.query(models.Donation).filter(models.Donation.id==donation_id).first()
    if not d: raise HTTPException(404,'Donación no encontrada')
    u=db.query(models.User).filter(models.User.id==d.donor_id).first()
    photos=db.query(models.Photo).filter(models.Photo.donation_id==d.id).order_by(models.Photo.uploaded_at.asc()).all()
    return {'donation':d,'donor':{'id':u.id,'username':u.username,'name':f'{u.first_name} {u.last_name}'.strip(),'reputation_score':u.reputation_score,'ratings_count':u.ratings_count},'photos':photos}
@router.post('/{donation_id}/photos')
def add_photo(donation_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    d=db.query(models.Donation).filter(models.Donation.id==donation_id).first()
    if not d: raise HTTPException(404,'Donación no encontrada')
    if d.donor_id!=user.id: raise HTTPException(403,'No podés modificar esta publicación')
    if image.content_type not in ('image/jpeg','image/png'): raise HTTPException(400,'La fotografía debe ser JPG o PNG')
    data=image.file.read(); ext='.jpg' if image.content_type=='image/jpeg' else '.png'; filename=f'{uuid.uuid4().hex}{ext}'; path=os.path.join(BASE_DIR,filename); open(path,'wb').write(data); p=models.Photo(donation_id=d.id,path=f'/uploads/{filename}',ai_result=ai.analyze_publication(d.title,d.description,d.resource_type,d.expiry_date)); db.add(p); db.commit(); db.refresh(p); return p
@router.post('/{donation_id}/favorite',response_model=dict)
def favorite(donation_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    if not db.query(models.Donation).filter(models.Donation.id==donation_id).first(): raise HTTPException(404,'Donación no encontrada')
    f=db.query(models.Favorite).filter(models.Favorite.user_id==user.id,models.Favorite.donation_id==donation_id).first()
    if f: db.delete(f); db.commit(); return {'favorite':False}
    db.add(models.Favorite(user_id=user.id,donation_id=donation_id)); db.commit(); return {'favorite':True}
