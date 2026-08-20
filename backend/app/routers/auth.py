import secrets
from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import auth,models,schemas
from ..database import get_db
router=APIRouter(prefix='/auth',tags=['Autenticación'])
@router.post('/register',response_model=schemas.UserOut,status_code=201)
def register(payload:schemas.UserCreate,db:Session=Depends(get_db)):
    if not payload.terms_accepted or not payload.privacy_accepted: raise HTTPException(400,'Debés aceptar Términos y Condiciones y Privacidad')
    if db.query(models.User).filter((models.User.username==payload.username)|(models.User.email==payload.email)).first(): raise HTTPException(400,'El usuario o email ya está registrado')
    token=secrets.token_urlsafe(24)
    u=models.User(**payload.model_dump(exclude={'password','terms_accepted','privacy_accepted'}),hashed_password=auth.hash_password(payload.password),verification_token=token,terms_accepted=True,privacy_accepted=True)
    # En desarrollo local dejamos la cuenta activa y exponemos la ruta de verificación en el mensaje de notificación.
    u.email_verified=True; u.status=models.AccountStatus.ACTIVE
    db.add(u); db.commit(); db.refresh(u); return u
@router.post('/login',response_model=schemas.Token)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    u=db.query(models.User).filter(models.User.username==form_data.username).first()
    if not u or not auth.verify_password(form_data.password,u.hashed_password): raise HTTPException(401,'Usuario o contraseña incorrectos',headers={'WWW-Authenticate':'Bearer'})
    return schemas.Token(access_token=auth.create_access_token({'sub':str(u.id)}))
@router.get('/me',response_model=schemas.UserOut)
def me(current_user:models.User=Depends(auth.get_current_user)): return current_user

@router.patch('/preferences')
def preferences(notification_frequency:str='inmediata',notification_types:str='match,message,expiry,delivery,rating',db:Session=Depends(get_db),user:models.User=Depends(auth.get_current_user)):
    user.notification_frequency=notification_frequency; user.notification_types=notification_types; db.commit(); return {'notification_frequency':user.notification_frequency,'notification_types':user.notification_types}
