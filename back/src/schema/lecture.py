from pydantic import BaseModel, Field
from typing import List, Optional

class LectureBase(BaseModel):
    year_level: Optional[str]
    curriculum: Optional[str]
    course_category: Optional[str]
    course_code: Optional[str]
    course_name: Optional[str]
    professor_name: Optional[str]
    campus: Optional[str]
    day_time: Optional[str]
    classroom: Optional[str]
    credits: Optional[float]
    lecture_type: Optional[str]
    lecture_category: Optional[str]
    course_type: Optional[str]
    offering_college: Optional[str]
    offering_department: Optional[str]
    intensive_semester: Optional[str]
    notes: Optional[str]

class LectureCreate(LectureBase):
    pass

class Lecture(LectureBase):
    id: int

    class Config:
        orm_mode = True

class LectureUpdate(LectureBase):
    pass