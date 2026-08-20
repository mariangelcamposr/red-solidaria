import os
from datetime import datetime,timedelta
from typing import Optional
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models
from .database import get_db
SECRET_KEY=os.getenv('SECRET_KEY','dev-only-change-this-secret-key')
ALGORITHM='HS256'; ACCESS_TOKEN_EXPIRE_MINUTES=60*24
pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto'); oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/auth/login')
def hash_password(password:str)->str:return pwd_context.hash(password)
def verify_password(plain_password:str,hashed_password:str)->bool:return pwd_context.verify(plain_password,hashed_password)
def create_access_token(data:dict,expires_delta:Optional[timedelta]=None)->str:
    payload=data.copy(); payload['exp']=datetime.utcnow()+(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)); return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db))->models.User:
    exc=HTTPException(status_code=401,detail='No se pudo validar las credenciales',headers={'WWW-Authenticate':'Bearer'})
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM]); user_id=payload.get('sub')
        if user_id is None: raise exc
    except (JWTError,ValueError): raise exc
    user=db.query(models.User).filter(models.User.id==int(user_id)).first()
    if not user or user.status==models.AccountStatus.SUSPENDED: raise exc
    return user
def require_roles(*roles):
    def dependency(user:models.User=Depends(get_current_user)):
        allowed={r.value if isinstance(r,models.UserRole) else r for r in roles}
        if user.role.value not in allowed: raise HTTPException(status_code=403,detail='No tenés permisos para esta operación')
        return user
    return dependency
