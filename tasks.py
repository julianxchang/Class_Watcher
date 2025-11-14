import requests
from bs4 import BeautifulSoup
import re, os, time, gc
from app.utils import get_watched_department, notify_students, fetch_department

def run_requests():
    i = 0
    while True:
        print(f"Starting course check #{i+1}...")
        run_task()
        i += 1
        time.sleep(120)  # check every 2 minutes

def run_task():
    pid = os.getpid()
    print(f"[PID {pid}] Starting check_courses task...")
    # Dictionary mapping department to another dictionary where key is course number and value is list of open class codes
    found = {}
    watched_departments = get_watched_department()

    print("Watched departments and courses:", watched_departments)

    for department in watched_departments:
        found[department] = {}
        html = fetch_department(department)
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all(class_='course-list')
        if not tables:
            print(f"No tables found for department {department}")
            continue
        table = tables[0].find_all('tr')
        i = 0
        while i < len(table):
            checkRow = table[i].find(class_="CourseTitle")  # first check if this contains Course Titla
            if checkRow:
                text = checkRow.get_text().lower()
                for course in watched_departments[department]:
                    pattern = rf"{department.lower()}\s+{course.lower()}\s+"
                    if re.search(pattern, text):
                        print(f">>> Matched course: {department} {course}")
                        j = i + 1
                        while j < len(table):
                            course_titles = table[j].find_all(class_="CourseTitle")
                            if course_titles:
                                i = j - 1
                                break
                            rows = table[j].find_all('td')
                            if rows:
                                print([row.text for row in rows])
                                if len(rows) > 10 and rows[1].text == "Lec" and rows[-1].text == "OPEN":
                                    classCode = rows[0].text
                                    print(f"Found open lecture: {classCode}")
                                    if course in found[department]:
                                        found[department][course].append(classCode)
                                    else:
                                        found[department][course] = [classCode]
                            j += 1
            i += 1
    if found:
        notify_students(found)
    del html, soup, tables, table
    gc.collect()

if __name__ == "__main__":
    run_requests()