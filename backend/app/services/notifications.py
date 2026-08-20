from datetime import datetime,timedelta
from .. import models

def scan_expiry(db):
    now=datetime.utcnow(); limit=now+timedelta(days=14)
    donations=db.query(models.Donation).filter(models.Donation.status.in_([models.DonationStatus.VISIBLE,models.DonationStatus.MATCHED]),models.Donation.expiry_date!=None,models.Donation.expiry_date<=limit).all()
    for d in donations:
        if d.expiry_date<now: d.status=models.DonationStatus.EXPIRED
        else:
            exists=db.query(models.Notification).filter(models.Notification.user_id==d.donor_id,models.Notification.kind=='expiry',models.Notification.message.like(f'%#{d.id}%')).first()
            if not exists:
                days=max(0,(d.expiry_date.date()-now.date()).days)
                db.add(models.Notification(user_id=d.donor_id,kind='expiry',title='Producto próximo a vencer',message=f'La donación #{d.id} vence en {days} día(s).'))
    db.commit()
