from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db

router=APIRouter(prefix='/matches',tags=['Coincidencias'])

@router.get('/me',response_model=list[schemas.MatchOut])
def my_matches(db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    """
    Devuelve las coincidencias relevantes para el usuario desde ambos roles:

    - Solicitante: sus propias coincidencias con donaciones de otros usuarios.
    - Donante: coincidencias sobre sus propias donaciones, pero solo cuando el
      solicitante ya las contactó (o la conversación/entrega ya está en curso).

    De esta forma, cuando un solicitante pulsa "Contactar donante", el donante
    puede ver la misma coincidencia y abrir la conversación.
    """
    requester_items = (
        db.query(models.Match)
        .join(models.Donation, models.Match.donation_id == models.Donation.id)
        .filter(
            models.Match.requester_id == user.id,
            models.Donation.donor_id != user.id,
        )
    )

    donor_items = (
        db.query(models.Match)
        .join(models.Donation, models.Match.donation_id == models.Donation.id)
        .filter(
            models.Donation.donor_id == user.id,
            models.Match.requester_id != user.id,
            models.Match.status.in_([
                models.MatchStatus.CONTACTED,
                models.MatchStatus.COORDINATING,
                models.MatchStatus.DELIVERED,
                models.MatchStatus.CLOSED,
            ]),
        )
    )

    items = (
        requester_items.union(donor_items)
        .order_by(models.Match.score.desc(), models.Match.created_at.desc())
        .all()
    )

    # Solo las coincidencias que pertenecen al flujo del solicitante pasan
    # de "notificada" a "visualizada". El donante no debe alterar este estado
    # simplemente por consultar sus coincidencias.
    changed = False
    for m in items:
        if m.requester_id == user.id and m.status == models.MatchStatus.NOTIFIED:
            m.status = models.MatchStatus.VIEWED
            changed = True

    if changed:
        db.commit()

    return items


@router.post('/{match_id}/contact',response_model=schemas.MatchOut)
def contact(match_id:int,db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    m=db.query(models.Match).filter(models.Match.id==match_id).first()
    if not m: raise HTTPException(404,'Coincidencia no encontrada')
    d=db.query(models.Donation).filter(models.Donation.id==m.donation_id).first()
    if user.id!=m.requester_id: raise HTTPException(403,'No podés contactar por esta coincidencia')
    if d.donor_id == user.id: raise HTTPException(400,'No podés contactar una donación propia')
    if d.status not in (models.DonationStatus.VISIBLE,models.DonationStatus.MATCHED): raise HTTPException(400,'La donación ya no está disponible')
    m.status=models.MatchStatus.CONTACTED
    db.add(models.Notification(
        user_id=d.donor_id,
        kind='contact',
        title='Nuevo interesado',
        message=f'Un usuario contactó tu donación #{d.id}.'
    ))
    db.commit()
    db.refresh(m)
    return m
