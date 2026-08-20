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
        # Un usuario no puede ser donante y solicitante de su propia coincidencia.
        if donation.donor_id == req.requester_id:
            continue
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


def cleanup_self_matches(db: Session):
    """Limpia coincidencias históricas inválidas sin romper FK con transacciones.

    Una coincidencia puede estar referenciada por Transaction.match_id. En ese caso
    no se puede eliminar físicamente porque PostgreSQL protege la integridad
    referencial. Se marca como CLOSED. Las coincidencias inválidas que no tienen
    transacciones asociadas sí se eliminan.
    """
    self_matches = (
        db.query(models.Match)
        .join(models.Donation, models.Match.donation_id == models.Donation.id)
        .filter(models.Donation.donor_id == models.Match.requester_id)
        .all()
    )

    if not self_matches:
        return

    affected_donation_ids = {m.donation_id for m in self_matches}
    match_ids = [m.id for m in self_matches]

    # No eliminar Matches que ya estén referenciados por una Transaction.
    referenced_match_ids = {
        row[0]
        for row in db.query(models.Transaction.match_id)
        .filter(models.Transaction.match_id.in_(match_ids))
        .all()
    }

    for match in self_matches:
        if match.id in referenced_match_ids:
            # Preservamos la fila para satisfacer transactions.match_id.
            # CLOSED hace que deje de considerarse una coincidencia activa.
            match.status = models.MatchStatus.CLOSED
        else:
            db.delete(match)

    db.flush()

    for donation_id in affected_donation_ids:
        donation = db.query(models.Donation).filter(models.Donation.id == donation_id).first()
        if not donation or donation.status != models.DonationStatus.MATCHED:
            continue

        valid_match = (
            db.query(models.Match)
            .join(models.Donation, models.Match.donation_id == models.Donation.id)
            .filter(
                models.Match.donation_id == donation_id,
                models.Donation.donor_id != models.Match.requester_id,
                models.Match.status != models.MatchStatus.CLOSED,
            )
            .first()
        )
        if not valid_match:
            donation.status = models.DonationStatus.VISIBLE

    db.commit()
