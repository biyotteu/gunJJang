from sqlalchemy.orm import Session, contains_eager, joinedload
from schema.schedule import ScheduleRecommend, ScheduleRecommendResponse
from schema import lecture as lecture_schema
import models
from typing import List, Optional
from fastapi import HTTPException
import utils.maketime

def recommend_schedule(body:ScheduleRecommend,db: Session) -> ScheduleRecommendResponse:
    top5 = utils.maketime.recommend_schedule(body.want_class,body.except_weekday,body.except_time)
    res = []
    print(top5)
    for schedule in top5:
        lectures = []
        for l in schedule:
            lecture = db.query(models.Lecture).filter(models.Lecture.course_code == l).first()
            lectures.append(lecture)
        # lectures = db.query(models.Lecture).filter(models.Lecture.course_code in schedule).all()
        res.append(lectures)

    print(res)
    return res