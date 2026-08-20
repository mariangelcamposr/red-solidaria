from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/admin',tags=['Administración'])
def admin(user:models.User=Depends(auth.get_current_user)):
    if user.role!=models.UserRole.ADMIN: raise HTTPException(403,'Solo administradores')
    return user
@router.get('/users')
def users(db:Session=Depends(get_db),_:models.User=Depends(admin)): return db.query(models.User).order_by(models.User.created_at.desc()).all()
@router.patch('/users/{user_id}/status')
def user_status(user_id:int,status:str,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    u=db.query(models.User).filter(models.User.id==user_id).first()
    if not u: raise HTTPException(404,'Usuario no encontrado')
    u.status=status; db.commit(); return {'ok':True}
@router.get('/categories')
def list_categories(db:Session=Depends(get_db),_:models.User=Depends(admin)): return db.query(models.CatalogCategory).all()
@router.post('/categories',response_model=schemas.CategoryOut)
def add_category(payload:schemas.CategoryCreate,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    c=models.CatalogCategory(**payload.model_dump()); db.add(c); db.commit(); db.refresh(c); return c
@router.patch('/categories/{category_id}')
def toggle_category(category_id:int,active:bool,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    c=db.query(models.CatalogCategory).filter(models.CatalogCategory.id==category_id).first(); c.active=active; db.commit(); return c
@router.patch('/users/{user_id}')
def update_user(user_id:int,role:str=None,status:str=None,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    u=db.query(models.User).filter(models.User.id==user_id).first()
    if not u: raise HTTPException(404,'Usuario no encontrado')
    if role:
        u.role=models.UserRole(role)
    if status:
        u.status=models.AccountStatus(status)
    db.commit(); return u

@router.delete('/categories/{category_id}')
def delete_category(category_id:int,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    c=db.query(models.CatalogCategory).filter(models.CatalogCategory.id==category_id).first(); c.active=False; db.commit(); return {'ok':True}

@router.get('/campaigns')
def campaigns(db:Session=Depends(get_db),_:models.User=Depends(admin)): return db.query(models.Campaign).order_by(models.Campaign.created_at.desc()).all()
@router.post('/campaigns',response_model=schemas.CampaignOut)
def add_campaign(payload:schemas.CampaignCreate,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    c=models.Campaign(**payload.model_dump()); db.add(c); db.commit(); db.refresh(c); return c
@router.patch('/campaigns/{campaign_id}')
def update_campaign(campaign_id:int,active:bool,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    c=db.query(models.Campaign).filter(models.Campaign.id==campaign_id).first(); c.active=active; db.commit(); return c

@router.delete('/campaigns/{campaign_id}')
def delete_campaign(campaign_id:int,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    c=db.query(models.Campaign).filter(models.Campaign.id==campaign_id).first(); db.delete(c); db.commit(); return {'ok':True}

@router.get('/partners')
def partners(db:Session=Depends(get_db),_:models.User=Depends(admin)): return db.query(models.BusinessPartner).all()
@router.post('/partners',response_model=schemas.PartnerOut)
def add_partner(payload:schemas.PartnerCreate,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    p=models.BusinessPartner(**payload.model_dump()); db.add(p); db.commit(); db.refresh(p); return p
@router.patch('/partners/{partner_id}')
def update_partner(partner_id:int,active:bool,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    p=db.query(models.BusinessPartner).filter(models.BusinessPartner.id==partner_id).first(); p.active=active; db.commit(); return p

@router.delete('/partners/{partner_id}')
def delete_partner(partner_id:int,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    p=db.query(models.BusinessPartner).filter(models.BusinessPartner.id==partner_id).first(); db.delete(p); db.commit(); return {'ok':True}

@router.patch('/memberships/{membership_id}')
def update_membership(membership_id:int,status:str,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    m=db.query(models.Membership).filter(models.Membership.id==membership_id).first(); m.status=status; db.commit(); return m

@router.get('/memberships')
def memberships(db:Session=Depends(get_db),_:models.User=Depends(admin)): return db.query(models.Membership).all()
@router.post('/memberships',response_model=schemas.MembershipOut)
def add_membership(payload:schemas.MembershipCreate,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    m=models.Membership(**payload.model_dump()); db.add(m); db.commit(); db.refresh(m); return m
@router.delete('/donations/{donation_id}')
def cancel_donation(donation_id:int,db:Session=Depends(get_db),_:models.User=Depends(admin)):
    d=db.query(models.Donation).filter(models.Donation.id==donation_id).first(); d.status=models.DonationStatus.CANCELLED; db.commit(); return {'ok':True}
@router.get('/reports/impact')
def impact(db:Session=Depends(get_db),_:models.User=Depends(admin)):
    donations=db.query(models.Donation).all(); tx=db.query(models.Transaction).all(); matches=db.query(models.Match).all(); ratings=db.query(models.Rating).all()
    bycat={}
    for d in donations: bycat[d.category]=bycat.get(d.category,0)+1
    return {'total_donations':len(donations),'completed_donations':sum(d.status==models.DonationStatus.COMPLETED for d in donations),'estimated_pets_benefited':sum(int(max(d.quantity,1)) for d in donations if d.status==models.DonationStatus.COMPLETED),'categories':bycat,'users_total':db.query(models.User).count(),'ratings_average':round(sum(r.score for r in ratings)/len(ratings),2) if ratings else 0,'successful_match_rate':round(sum(t.status==models.TransactionStatus.COMPLETED for t in tx)/len(matches)*100,2) if matches else 0,'transactions_completed':sum(t.status==models.TransactionStatus.COMPLETED for t in tx)}
