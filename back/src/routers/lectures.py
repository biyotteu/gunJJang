from sqlalchemy.orm import Session, contains_eager, joinedload
from schema import lecture as lecture_schema
from crud import lecture as lecture_cud
import models
import database
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/list/")
def get_lectures(lecture_name:Optional[str]=None,db: Session = Depends(database.get_db)):
    return lecture_cud.get_lecture_by_name(db, lecture_name)
