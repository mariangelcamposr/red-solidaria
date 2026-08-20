import json, math
from sqlalchemy.orm import Session
from .. import models

def distance_km(lat1,lon1,lat2,lon2):
    if None in (lat1,lon1,lat2,lon2): return None
    r=6371.0; p1=math.radians(lat1); p2=math.radians(lat2); dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(2*r*math.asin(math.sqrt(a)),2)

def calculate_score(donation,req):
    score=0; criteria=[]
    if donation.resource_type.strip().lower()==req.resource_type.strip().lower(): score+=0.15; criteria.append('tipo coincidente')
    if donation.category.strip().lower()==req.category.strip().lower(): score+=0.30; criteria.append('categoría coincidente')
    dist=distance_km(donation.latitude,donation.longitude,req.latitude,req.longitude)
    if dist is not None:
        if dist<=5: score+=0.25; criteria.append('ubicación cercana')
        elif dist<=25: score+=0.15; criteria.append('ubicación próxima')
    elif donation.location.strip().lower()==req.location.strip().lower(): score+=0.25; criteria.append('ubicación coincidente')
    if donation.quantity>=req.quantity: score+=0.15; criteria.append('cantidad suficiente')
    if donation.expiry_date:
        days=(donation.expiry_date.date()-__import__('datetime').datetime.utcnow().date()).days
        if days<0: score-=0.50; criteria.append('vencida')
        elif days<=14: score+=0.10; criteria.append('próxima a vencer')
    priority_bonus={'alta':0.05,'media':0.03,'baja':0.0}.get(req.priority.value,0)
    score+=priority_bonus; criteria.append(f'prioridad {req.priority.value}')
    if donation.is_urgent: score+=0.05; criteria.append('donación urgente')
    return max(0,round(min(score,1.0),2)),dist,criteria

def run_matching_for_donation(db:Session,donation):
    reqs=db.query(models.Request).filter(models.Request.status.in_([models.RequestStatus.OPEN,models.RequestStatus.IN_PROGRESS])).all(); created=[]
    for req in reqs:
        score,dist,criteria=calculate_score(donation,req)
        if score<=0: continue
        exists=db.query(models.Match).filter(models.Match.donation_id==donation.id,models.Match.request_id==req.id).first()
        if exists: continue
        m=models.Match(donation_id=donation.id,request_id=req.id,requester_id=req.requester_id,score=score,distance_km=dist,criteria=json.dumps(criteria,ensure_ascii=False),status=models.MatchStatus.NOTIFIED)
        db.add(m); created.append(m)
        db.add(models.Notification(user_id=req.requester_id,kind='match',title='Nueva coincidencia',message=f'Encontramos una donación compatible con tu solicitud #{req.id}.'))
    if created: donation.status=models.DonationStatus.MATCHED
    db.commit()
    for m in created: db.refresh(m)
    return created
