from sqlalchemy import create_engine
from config import get_settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse
from models import Base, Lecture, Schedule
from utils.crypt import get_password_hash
from datetime import datetime
import pandas as pd
from tqdm import tqdm

settings = get_settings()

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{}:{}@{}:{}/{}".format(
    settings.MYSQL_USER,
    urllib.parse.quote_plus(settings.MYSQL_PASSWORD), # Add this line to escape special characters in the password (e.g. @, /, etc.)
    settings.MYSQL_HOST,
    settings.MYSQL_PORT,
    settings.MYSQL_DATABASE,
)

# SQLALCHEMY_DATABASE_URL = "sqlite:///db\\course.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    session = SessionLocal()
    Base.metadata.create_all(bind=engine)

    # session.query(Schedule).delete()
    session.query(Lecture).delete()
    session.commit()
    
    df = pd.read_excel('../data/timetable.xlsx')
    df = df.where(pd.notnull(df), None)

    print("Inserting data into the database")
    
    # Inserting data into the database
    lectures = []
    count = 0
    for row in tqdm(df.itertuples(index=False), total=df.shape[0]):
        # print(row._fields)
        # print(row)
        lecture = Lecture( 
            year_level=row._1,
            curriculum=row.교과과정,
            course_category=row.교과영역구분,
            course_code=row.학수강좌번호,
            course_name=row.교과목명,
            professor_name=row.교원명,
            campus=row.수업캠퍼스,
            day_time=row._8,
            classroom=row.강의실,
            credits=row.학점,
            lecture_type=row.강의유형,
            lecture_category=row.강의종류,
            course_type=row.이수구분,
            offering_college=row.개설대학,
            offering_department=row._24,
            intensive_semester=row.집중이수학기구분,
            notes=row.비고
        )
        lectures.append(lecture)

    session.bulk_save_objects(lectures)
    session.commit()

    # Reading CSV files and inserting data into the database

    # Load schedules
    # lectures = session.query(Lecture).all()
    # print("lecture length",len(lectures))
    # lecture_dict = {lecture.course_code: lecture for lecture in lectures}

    # for i in range(10):
    #     file_path = f'../data/valid_schedules_{i}.csv'
    #     df = pd.read_csv(file_path)
    #     df = df.where(pd.notnull(df), None)
        
    #     schedules = []
    #     for row in tqdm(df.itertuples(index=False), total=df.shape[0]):
    #         schedule = Schedule(
    #             total_credit=row.Total_Credits,
    #             total_time=row.Total_Time,
    #             time_score=row.Time_Score
    #         )
            
    #         for column in [row._4, row._5, row._6, row._7, row._8, row._8]:
    #             lecture = lecture_dict.get(column)
    #             if lecture:
    #                 schedule.lectures.append(lecture)

    #         session.add(schedule)
    #         # schedules.append(schedule)
        
    #     # session.bulk_save_objects(schedules)
    #     session.commit()

    session.close()
    

def test_db():
    session = SessionLocal()
    Base.metadata.create_all(bind=engine)

    s = session.query(Schedule).all()
    print("Test DB Success")
    for i in s:
        if len(i.lectures) > 0:
            print(i.total_time, i.total_credit, i.time_score, i.lectures)
    session.close()