from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
router=APIRouter(prefix='/catalogs',tags=['Catálogos'])
@router.get('/categories')
def categories(db:Session=Depends(get_db)):
    return db.query(models.CatalogCategory).filter(models.CatalogCategory.active==True).order_by(models.CatalogCategory.resource_type,models.CatalogCategory.name).all()
