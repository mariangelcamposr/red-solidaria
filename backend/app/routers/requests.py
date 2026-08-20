from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
from ..services import matching
router=APIRouter(prefix='/requests',tags=['Solicitudes'])
@router.post('',response_model=schemas.RequestOut,status_code=201)
def create_request(payload:schemas.RequestCreate,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    r=models.Request(requester_id=user.id,**payload.model_dump()); db.add(r); db.commit(); db.refresh(r)
    # Una nueva solicitud también busca donaciones ya disponibles.
    donations=db.query(models.Donation).filter(models.Donation.status.in_([models.DonationStatus.VISIBLE,models.DonationStatus.MATCHED])).all()
    for d in donations: matching.run_matching_for_donation(db,d)
    return r
@router.get('',response_model=list[schemas.RequestOut])
def my_requests(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    return db.query(models.Request).filter(models.Request.requester_id==user.id).order_by(models.Request.created_at.desc()).all()
@router.patch('/{request_id}/deactivate',response_model=schemas.RequestOut)
def deactivate(request_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    r=db.query(models.Request).filter(models.Request.id==request_id).first()
    if not r: raise HTTPException(404,'Solicitud no encontrada')
    if r.requester_id!=user.id and user.role!=models.UserRole.ADMIN: raise HTTPException(403,'No podés modificar esta solicitud')
    r.status=models.RequestStatus.CLOSED; db.commit(); db.refresh(r); return r

@router.post('/{request_id}/photo')
def add_photo(request_id:int, image:__import__('fastapi').UploadFile=__import__('fastapi').File(...), db:Session=Depends(get_db), user:models.User=Depends(auth.get_current_user)):
    import os,uuid
    r=db.query(models.Request).filter(models.Request.id==request_id).first()
    if not r: raise HTTPException(404,'Solicitud no encontrada')
    if r.requester_id!=user.id: raise HTTPException(403,'No podés modificar esta solicitud')
    if image.content_type not in ('image/jpeg','image/png'): raise HTTPException(400,'La fotografía debe ser JPG o PNG')
    base=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../uploads')); os.makedirs(base,exist_ok=True); ext='.jpg' if image.content_type=='image/jpeg' else '.png'; filename=f'{uuid.uuid4().hex}{ext}'; path=os.path.join(base,filename); open(path,'wb').write(image.file.read()); r.image_path=f'/uploads/{filename}'; db.commit(); return {'image_path':r.image_path}
