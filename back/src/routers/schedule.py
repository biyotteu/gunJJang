from sqlalchemy.orm import Session, contains_eager, joinedload
from schema.schedule import ScheduleRecommend, ScheduleRecommendResponse
from crud import schedule as schedule_cud
import models
import database
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.post("/recommend")
def recommend_schedule(body:ScheduleRecommend,db: Session = Depends(database.get_db)) -> ScheduleRecommendResponse:
    return {
        "top5":schedule_cud.recommend_schedule(body,db)
    }