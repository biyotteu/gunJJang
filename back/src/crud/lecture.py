from sqlalchemy.orm import Session, contains_eager, joinedload
from schema import lecture as lecture_schema
import models
from typing import List, Optional
from fastapi import HTTPException

def get_lecture_by_name(db: Session, course_name: Optional[str]) -> Optional[lecture_schema.Lecture]:
    if(course_name is None):
        return db.query(models.Lecture).limit(10).all()
    return db.query(models.Lecture).filter(models.Lecture.course_name.like(f"%{course_name}%")).all()




