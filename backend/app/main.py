import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models,auth
from .services.matching import cleanup_self_matches
from .database import Base,engine,SessionLocal
from .routers import auth as auth_router,chat,donations,matches,ratings,requests,transactions,notifications,dashboard,search,assistant,catalogs,admin,support
Base.metadata.create_all(bind=engine)
app=FastAPI(title='Red Solidaria de Donaciones para Mascotas',description='Plataforma colaborativa para donar y solicitar medicamentos, alimentos, accesorios e insumos para mascotas.',version='2.1.3.1')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173','https://red-solidaria-fe.onrender.com'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
os.makedirs('uploads',exist_ok=True); app.mount('/uploads',StaticFiles(directory='uploads'),name='uploads')
for r in (auth_router.router,donations.router,requests.router,matches.router,chat.router,transactions.router,ratings.router,notifications.router,dashboard.router,search.router,assistant.router,catalogs.router,admin.router,support.router): app.include_router(r)

def seed():
    db:Session=SessionLocal()
    if db.query(models.CatalogCategory).count()==0:
        seed_data=[('medicamento','Medicamentos'),('medicamento','Antiparasitarios'),('alimento','Alimento seco'),('alimento','Alimento húmedo'),('accesorio','Collares y correas'),('accesorio','Camas'),('producto de higiene','Higiene'),('otro','Otros')]
        db.add_all([models.CatalogCategory(resource_type=t,name=n) for t,n in seed_data])
    # El dominio .local puede ser rechazado por EmailStr como dominio reservado.
    # Usamos un dominio de desarrollo válido y, además, corregimos instalaciones
    # anteriores que ya tenían creado el admin con admin@donaciones.local.
    admin_email=os.getenv('ADMIN_EMAIL','admin@redsolidaria.app'); admin_user=os.getenv('ADMIN_USERNAME','admin'); admin_pass=os.getenv('ADMIN_PASSWORD','admin123')
    admin=db.query(models.User).filter(models.User.username==admin_user).first()
    if not admin:
        admin=db.query(models.User).filter(models.User.email==admin_email).first()
    if not admin:
        admin=db.query(models.User).filter(models.User.email=='admin@donaciones.local').first()
    if not admin:
        admin=models.User(username=admin_user,email=admin_email,hashed_password=auth.hash_password(admin_pass),first_name='Administrador',last_name='Sistema',phone='0000000000',address='Local',city='Local',state='Local',country='Local',role=models.UserRole.ADMIN,status=models.AccountStatus.ACTIVE,email_verified=True,terms_accepted=True,privacy_accepted=True)
        db.add(admin)
    else:
        # Migración ligera para la instalación local del curso.
        if admin.email == 'admin@donaciones.local':
            admin.email = admin_email
        admin.role=models.UserRole.ADMIN
        admin.status=models.AccountStatus.ACTIVE
        admin.email_verified=True
        admin.terms_accepted=True
        admin.privacy_accepted=True
    db.commit(); cleanup_self_matches(db); db.close()
seed()
@app.get('/')
def root(): return {'status':'ok','docs':'/docs','version':'2.1.3'}
@app.get('/health')
def health(): return {'status':'healthy'}
