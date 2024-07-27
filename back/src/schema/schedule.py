from pydantic import BaseModel, Field
from typing import List, Optional

from schema.lecture import Lecture


class ScheduleRecommend(BaseModel):
    want_class: set[str]
    except_weekday: set[str]
    except_time: set[str]

class ScheduleRecommendResponse(BaseModel):
    top5: List[List[Lecture]]

# class Schedule(BaseModel):
#     id: int
#     lecture_ids: List[str]
#     total_credit: int
#     total_time: str
#     time_score: float



# class LectureCreate(LectureBase):
#     pass

# class Lecture(LectureBase):
#     id: int
#     professor_id: Optional[int] = Field(..., nullable=True)

    # class Config:
    #     orm_mode = True

# class LectureUpdate(LectureBase):
#     pass