from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

lecture_schedule = Table('lecture_schedule', Base.metadata,
    Column('lecture_id', Integer, ForeignKey('lecture.id'), primary_key=True),
    Column('schedule_id', Integer, ForeignKey('schedule.id'), primary_key=True)
)

class Lecture(Base):
    __tablename__ = 'lecture'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    year_level = Column(String(255))  # 학년/가진급학년
    curriculum = Column(String(255))  # 교과과정
    course_category = Column(String(255))  # 교과영역구분
    course_code = Column(String(255))  # 학수강좌번호
    course_name = Column(String(255))  # 교과목명
    professor_name = Column(String(255))  # 교원명
    campus = Column(String(255))  # 수업캠퍼스
    day_time = Column(String(1023))  # 요일/시간
    classroom = Column(String(511))  # 강의실
    credits = Column(Float)  # 학점
    lecture_type = Column(String(255))  # 강의유형
    lecture_category = Column(String(255))  # 강의종류
    course_type = Column(String(255))  # 이수구분
    offering_college = Column(String(255))  # 개설대학
    offering_department = Column(String(255))  # 개설학과/전공
    intensive_semester = Column(String(255))  # 집중이수학기구분
    notes = Column(String(511))  # 비고

    schedules = relationship('Schedule', secondary=lecture_schedule, back_populates='lectures')


class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    lecture_ids = Column(String(255))
    total_credit = Column(Integer)
    total_time = Column(String(1023))
    time_score = Column(Float)
    lectures = relationship('Lecture', secondary=lecture_schedule, back_populates='schedules')



    
    