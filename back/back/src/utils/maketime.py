# pip install pandas openpyxl


import pandas as pd

# 필요 라이브러리 불러오기
import os
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.font_manager")

class Course:
    def __init__(self, course_id, course_name, curriculum, years, is_english, times, credits):
        self.course_id = course_id
        self.course_name = course_name.replace(' ', '')
        self.curriculum = curriculum
        self.years = years  # List of eligible years
        self.is_english = is_english
        self.times = times  # 7x260 boolean array
        self.credits = credits

def parse_time_schedule(time_str):
    times = [[False] * 260 for _ in range(7)]
    days = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4, '토': 5, '일': 6}
    if pd.isna(time_str):
        return times
    for part in time_str.split(','):
        day_part, time_part = part.split('/')
        day_index = days[day_part[0]]
        start_time, end_time = time_part.split('-')
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        start_block = ((start_hour - 9) * 60 + start_minute) // 5
        end_block = ((end_hour - 9) * 60 + end_minute) // 5
        for block in range(start_block, end_block):
            times[day_index][block] = True
    return times

def parse_years(year_str):
    if year_str == '전체학년':
        return [1, 2, 3, 4]
    years = []
    if '1학년' in year_str:
        years.append(1)
    if '2학년' in year_str:
        years.append(2)
    if '3학년' in year_str:
        years.append(3)
    if '4학년' in year_str:
        years.append(4)
    return years

def read_excel_file(filename):
    df = pd.read_excel(filename)
    courses = []
    for _, row in df.iterrows():
        course_id = row['학수강좌번호']
        course_name = row['교과목명'].replace(' ', '')
        curriculum = row['교과과정']
        years = parse_years(row['학년/가진급학년'])
        is_english = row['원어강의'] == 'Y'
        times = parse_time_schedule(row['요일/시간'])
        credits = int(row['학점']) if not pd.isna(row['학점']) else 0
        courses.append(Course(course_id, course_name, curriculum, years, is_english, times, credits))
    return courses

def read_completed_courses(filename):
    df = pd.read_excel(filename)
    completed_courses = set()
    f_courses = set()
    for _, row in df.iterrows():
        course_id_prefix = row['학수강좌번호'].split('-')[0]
        course_name = row['교과목명'].strip().replace(" ", "")
        credits = row['학점']
        if row['등급'] == 'F':
            f_courses.add(course_name)
        completed_courses.add((course_id_prefix, course_name, credits))  # 학점도 추가
    return completed_courses, f_courses


#시간 비교
def is_time_conflict(schedule, course_times):
    for day in range(7):
        for time in range(260):
            if schedule[day][time] and course_times[day][time]:
                return True
    return False


#시간표에 과목 추가
def add_course_to_schedule(schedule, course_times):
    for day in range(7):
        for time in range(260):
            if course_times[day][time]:
                schedule[day][time] = True

#우선순위 계산
def calculate_priority_score(course, f_courses, priority_groups, msc_courses, selected_courses, group_limits):
    course_name = course.course_name.strip().replace(" ", "")

    if course_name in f_courses:
        return 10

    for group_name, group in priority_groups.items():
        group_courses = [c.strip().replace(" ", "") for c in group]
        if course_name in group_courses:
            if group_limits[group_name] > 0:
                return 8
            else:
                return 0  # 그룹 내에서 이미 최대 선택된 경우 0점 부여

    if course_name in [c.strip().replace(" ", "") for c in msc_courses]:
        if group_limits["MSC"] > 0:
            return 6
        else:
            return 0  # MSC 그룹 내에서 학점을 초과한 경우 0점 부여

    if hasattr(course, 'curriculum') and course.curriculum == '전공':
        return 7

    return 0

#시간표 작성
def generate_top_schedules(selected_courses, courses, completed_courses, f_courses, priority_groups, msc_courses, num_courses, group_limits, top_n=100, max_attempts=1000):
    import random

    # 과목 점수에 따라 정렬
    course_scores = {}
    for course in courses:
        course_scores[course.course_name.strip().replace(" ", "")] = calculate_priority_score(course, f_courses, priority_groups, msc_courses, [], group_limits)

    courses = sorted(courses, key=lambda x: course_scores[x.course_name.strip().replace(" ", "")], reverse=True)
    courses = courses[:top_n]

    all_schedules = []
    attempt_counter = 0

    def is_time_conflict_with_selected(selected_courses, new_course):
        for selected_course in selected_courses:
            if is_time_conflict(selected_course.times, new_course.times):
                return True
        return False

    while attempt_counter < max_attempts:
        random.shuffle(courses)
        attempt_counter += 1
        current_selected_courses = selected_courses[:]
        current_num_courses = len(current_selected_courses)
        current_group_limits = group_limits.copy()
        taken_courses_by_group = {group_name: [] for group_name in priority_groups}
        taken_courses_by_group["MSC"] = []

        for course in current_selected_courses:
            course_name = course.course_name.strip().replace(" ", "")
            for group_name, group in priority_groups.items():
                group_courses = [c.strip().replace(" ", "") for c in group]
                if course_name in group_courses:
                    current_group_limits[group_name] -= 1
                    taken_courses_by_group[group_name].append(course.course_name)

            if course_name in [c.strip().replace(" ", "") for c in msc_courses]:
                current_group_limits["MSC"] -= course.credits
                taken_courses_by_group["MSC"].append(course.course_name)

        for course in courses:
            course_name = course.course_name.strip().replace(" ", "")
            if current_num_courses >= num_courses:
                break
            if any(course_name == completed_course_name for completed_course_name in completed_courses):
                continue
            if any(course_name == selected_course.course_name.strip().replace(" ", "") for selected_course in current_selected_courses):
                continue
            if is_time_conflict_with_selected(current_selected_courses, course):
                continue

            added_to_group = False
            for group_name, group in priority_groups.items():
                group_courses = [c.strip().replace(" ", "") for c in group]
                if course_name in group_courses:
                    if current_group_limits[group_name] > 0:
                        current_group_limits[group_name] -= 1
                        taken_courses_by_group[group_name].append(course.course_name)
                        added_to_group = True

            if course_name in [c.strip().replace(" ", "") for c in msc_courses]:
                if current_group_limits["MSC"] >= course.credits:
                    current_group_limits["MSC"] -= course.credits
                    taken_courses_by_group["MSC"].append(course.course_name)
                    added_to_group = True

            if added_to_group:
                current_selected_courses.append(course)
                current_num_courses += 1

        score = sum(calculate_priority_score(course, f_courses, priority_groups, msc_courses, current_selected_courses, current_group_limits) for course in current_selected_courses)
        all_schedules.append((current_selected_courses, score, taken_courses_by_group.copy(), current_group_limits.copy()))

    return all_schedules, attempt_counter

# def create_timetable(schedule, selected_courses):
#     fig, ax = plt.subplots(figsize=(10, 8))  # 크기 조정
#     days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
#     times = [f'{hour:02d}:00' for hour in range(9, 24)]

#     for day in range(8):
#         ax.axvline(x=day, color='k', linewidth=1)
#     for time in range(16):
#         ax.axhline(y=time, color='k', linewidth=1)

#     ax.set_xticks([i + 0.5 for i in range(7)])
#     ax.set_xticklabels(days)
#     ax.set_yticks([i + 0.5 for i in range(15)])
#     ax.set_yticklabels(times)
#     ax.invert_yaxis()

#     colors = plt.cm.get_cmap('hsv', len(selected_courses))

#     for idx, course in enumerate(selected_courses):
#         course_name_written = False
#         for day in range(7):
#             for time in range(260):
#                 if course.times[day][time]:
#                     start_block = time // 12
#                     end_block = (time % 12) / 12
#                     rect = patches.Rectangle((day, start_block), 1, end_block, edgecolor='black', facecolor=colors(idx), alpha=0.5)
#                     ax.add_patch(rect)
#                     if not course_name_written:
#                         ax.text(day + 0.5, start_block + end_block / 2, f"{course.course_name} ({course.course_id})", ha='center', va='center', fontsize=8, color='black')
#                         course_name_written = True

#     plt.show()

#대체 시간 찾기
def find_alternative_courses(course, all_courses, selected_courses, completed_courses):
    alternatives = []
    for candidate in all_courses:
        if candidate.course_id == course.course_id:
            continue
        if candidate.course_name.strip().replace(" ", "") == course.course_name.strip().replace(" ", ""):
            continue
        if any(candidate.course_name.strip().replace(" ", "") == selected_course.course_name.strip().replace(" ", "") for selected_course in selected_courses):
            continue
        if any(candidate.course_name.strip().replace(" ", "") == completed_course_name for _, completed_course_name, _ in completed_courses):
            continue
        if candidate.times != course.times:
            continue
        alternatives.append(candidate)
        if len(alternatives) >= 5:
            break
    return alternatives

def print_schedule(idx, selected_courses, score, taken_courses_by_group, current_group_limits, completed_courses, f_courses, priority_groups, msc_courses, all_courses):
    print(f"\nTop {idx+1} Schedule (Score: {score}):")  # 각 스케줄의 점수를 출력

    for course in selected_courses:
        course_score = calculate_priority_score(course, f_courses, priority_groups, msc_courses, selected_courses, current_group_limits)
        print(f"{course.course_name} ({course.course_id}) - {course.credits} credits - Score: {course_score}")

    # 현재 group_limits 값 출력
    print("Current Group Limits:")
    for group_name, limit in current_group_limits.items():
        print(f"{group_name}: {limit}")

    # 해당 그룹에 수강한 과목들 출력 (이미 들은 과목 포함)
    print("Taken Courses by Group:")
    for group_name, group in priority_groups.items():
        completed_and_selected_courses = [course_name for _, course_name, _ in completed_courses if course_name in [c.strip().replace(" ", "") for c in group]]
        completed_and_selected_courses += [course.course_name for course in selected_courses if course.course_name.strip().replace(" ", "") in [c.strip().replace(" ", "") for c in group]]
        print(f"{group_name}: {', '.join(completed_and_selected_courses)}")

    # 전공 과목 출력
    print("전공 과목:")
    completed_and_selected_majors = [course_name for _, course_name, _ in completed_courses if course_name in [c.strip().replace(" ", "") for c in msc_courses] or course_name == '전공']
    completed_and_selected_majors += [course.course_name for course in selected_courses if course.course_name.strip().replace(" ", "") in [c.strip().replace(" ", "") for c in msc_courses] or course.curriculum == '전공']
    print(f"전공 과목: {', '.join(completed_and_selected_majors)}")

    # 시간표 시각화
    schedule = [[False] * 260 for _ in range(7)]  # 시간표 초기화
    for course in selected_courses:
        course_name = course.course_name.strip().replace(" ", "")
        if calculate_priority_score(course, f_courses, priority_groups, msc_courses, selected_courses, current_group_limits) > 0 and not any(course_name == completed_course_name for _, completed_course_name, _ in completed_courses):
            add_course_to_schedule(schedule, course.times)  # 시간표에 과목 추가
    # create_timetable(schedule, selected_courses)  # 시간표 시각화

    # 대체 과목 찾기 및 출력
    print("\nAlternative Courses:")
    for course in selected_courses:
        alternatives = find_alternative_courses(course, all_courses, selected_courses, completed_courses)
        print(f"\n{course.course_name} ({course.course_id}) - Alternatives:")
        for alternative in alternatives:
            print(f"  {alternative.course_name} ({alternative.course_id}) - {alternative.credits} credits")

def should_exclude_course(course, except_days):
    days = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4, '토': 5, '일': 6}
    for day_str in except_days:
        day_index = days[day_str]
        if any(course.times[day_index]):
            return True
    return False

def should_exclude_course_time(course, except_times):
    days = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4, '토': 5, '일': 6}
    for time_str in except_times:
        day_part, time_part = time_str.split('/')
        day_str = day_part[0]
        day_index = days[day_str]
        start_time, end_time = time_part.split('-')
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        start_block = ((start_hour - 9) * 60 + start_minute) // 5
        end_block = ((end_hour - 9) * 60 + end_minute) // 5
        for block in range(start_block, end_block):
            if course.times[day_index][block]:
                return True
    return False

def select_wanted_courses(courses, want_class):
    selected_courses = [course for course in courses if course.course_id in want_class]
    selected_course_ids = {course.course_id for course in selected_courses}
    selected_course_names = {course.course_name.strip().replace(" ", "") for course in selected_courses}
    return selected_courses, selected_course_ids, selected_course_names

def exclude_courses_by_criteria(courses, except_weekday, except_time):
    courses = [course for course in courses if not should_exclude_course(course, except_weekday)]
    courses = [course for course in courses if not should_exclude_course_time(course, except_time)]
    return courses

def update_group_limits(completed_courses, priority_groups, msc_courses, group_limits):
    for course_id_prefix, course_name, course_credits in completed_courses:
        for group_name, group in priority_groups.items():
            group_courses = [c.strip().replace(" ", "") for c in group]
            if course_name in group_courses:
                group_limits[group_name] -= 1
                if group_limits[group_name] < 0:
                    group_limits[group_name] = 0

        if course_name in [c.strip().replace(" ", "") for c in msc_courses]:
            group_limits["MSC"] -= course_credits
            if group_limits["MSC"] < 0:
                group_limits["MSC"] = 0
    return group_limits

def get_msc_courses():
    return ["미적분학및연습1", "미적분학및연습2", "확률및통계학", "공학선형대수학", "공학수학1", "이산수학", "물리학개론", "일반물리학실험1", "일반물리학실험2", "화학개론", "일반화학및실험1", "일반화학및실험2", "생물학개론", "일반생물학및실험1", "일반생물학및실험2", "지구환경과학", "프로그래밍기초와실습", "인터넷프로그래밍", "데이터프로그래밍기초와실습", "인공지능프로그래밍기초와실습"]

def get_priority_groups():
    return {
        "동국인성그룹": ["자아와명상1", "자아와명상2", "불교와인간"],
        "자기계발그룹": ["커리어 디자인", "기업가정신과리더십"],
        "사고와소통그룹1": ["디지털시대의글쓰기", "기술보고서작성및발표"],
        "사고와소통그룹2": ["Global English 1", "Global English 2", "Business English 1", "Business English 2"],
        "창의융합그룹": ["지혜와자비명작세미나", "존재와역사명작세미나", "경제와사회명작세미나", "자연과기술명작세미나", "문화와예술명작세미나"],
        "디지털리터러시그룹": ["디지털 기술과 사회의 이해", "프로그래밍 이해와 실습", "빅데이터와 인공지능의 이해"],
        "기본소양그룹": ["기술창조와특허", "공학경제", "공학윤리"]
    }

def get_initial_group_limits():
    return {
        "동국인성그룹": 3,
        "자기계발그룹": 2,
        "사고와소통그룹1": 1,
        "사고와소통그룹2": 1,
        "창의융합그룹": 1,
        "디지털리터러시그룹": 3,
        "기본소양그룹": 2,
        "MSC": 28  # MSC 그룹은 학점으로 설정
    }

def recommend_schedule(want_class,except_weekday,except_time) -> List[List[str]]:
    timetable_filename = '../data/timetable.xlsx'
    completed_courses_filename = '../data/student.xlsx'

    courses = read_excel_file(timetable_filename)
    completed_courses, f_courses = read_completed_courses(completed_courses_filename)

    # 우선순위 그룹 설정
    msc_courses = get_msc_courses()
    priority_groups = get_priority_groups()
    group_limits = get_initial_group_limits()

    num_courses = 6  # 수강 과목 수 설정
    max_attempts = 1000  # 최대 시도 횟수 설정
    top_n = 300  # 상위 n개 과목만 사용

    # want_class = {"RGC1010-21", "RGC1013-21"}  # 예시로 특정 학수번호 과목을 포함
    # except_weekday = {"금"}  # 예시로 금요일을 제외
    # except_time = {"월4.0-5.0/12:00-13:30", "수4.0-5.0/12:00-13:30"}  # 예시로 특정 시간을 제외

    # 이미 들은 과목 정보를 바탕으로 group_limits 업데이트
    group_limits = update_group_limits(completed_courses, priority_groups, msc_courses, group_limits)

    # 이미 수강한 과목명과 동일한 과목을 제거하는 전처리 과정
    completed_course_names = {course_name for _, course_name, _ in completed_courses}
    courses = [course for course in courses if course.course_name.strip().replace(" ", "") not in completed_course_names]

    # want_class에 있는 과목을 무조건 선택
    selected_courses, selected_course_ids, selected_course_names = select_wanted_courses(courses, want_class)

    # 선택한 과목을 제외한 나머지 과목 리스트 업데이트
    courses = [course for course in courses if course.course_id not in selected_course_ids]

    # 제외할 요일과 시간이 포함된 과목을 제거
    courses = exclude_courses_by_criteria(courses, except_weekday, except_time)

    # 모든 가능한 조합을 찾기 (최대 10,000번 시도)
    scored_schedules, attempt_counter = generate_top_schedules(selected_courses, courses, completed_courses, f_courses, priority_groups, msc_courses, num_courses, group_limits, top_n, max_attempts)

    scored_schedules.sort(key=lambda x: x[1], reverse=True)  # 점수 기준으로 스케줄을 정렬
    top_5_schedules = scored_schedules[:5]  # 상위 5개의 스케줄을 선택

    top_5 = []
    for sch in top_5_schedules:
        codes = []
        for course in sch[0]:
            codes.append(course.course_id)
        top_5.append(codes)

    return top_5
    # print(f"Total Attempts: {attempt_counter}")  # 총 시도 횟수를 출력
    # for idx, (selected_courses, score, taken_courses_by_group, current_group_limits) in enumerate(top_5_schedules):
    #     print_schedule(idx, selected_courses, score, taken_courses_by_group, current_group_limits, completed_courses, f_courses, priority_groups, msc_courses, courses)

if __name__ == "__main__":
    print(recommend_schedule({},{},{}))  # 메인 함수 실행

