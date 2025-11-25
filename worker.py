from bs4 import BeautifulSoup
import re, os, time
from app.utils import get_watched_department, notify_students, fetch_department, update_system_status

def run_task():
    pid = os.getpid()
    print(f"[PID {pid}] Starting check_courses task...")
    # Dictionary mapping department to another dictionary where key is course number and value is list of open class codes
    found = {}
    watched_departments = get_watched_department()

    print("Watched departments and courses:", watched_departments)

    for idx, department in enumerate(watched_departments):
        if idx > 0:
            time.sleep(5)  # 5 second delay between department fetches
        found[department] = {}
        print(f"Fetching department: {department}")
        html = fetch_department(department)
        if not html:
            print(f"Error fetching {department} department.")
            continue

        soup = BeautifulSoup(html, 'html.parser')

        tables = soup.find_all(class_='course-list')
        if not tables:
            print(f"No tables found for department {department}")
            del html, soup, tables
            continue
        table = tables[0].find_all('tr')
        i = 0

        while i < len(table):
            title_cell = table[i].find(attrs={'class': 'CourseTitle'})
            if title_cell:
                title_text = title_cell.get_text().lower()

                j = i + 1
                while j < len(table) and not table[j].find(attrs={'class': 'CourseTitle'}):
                    rows = table[j].find_all("td")
                    if not rows or len(rows) < 10:
                        j += 1
                        continue

                    class_code = rows[0].text
                    if class_code in watched_departments[department]:
                        print(f">>>Matched CLASS CODE: {class_code}")
                    class_type = rows[1].text
                    status = rows[-1].text

                    if status == "FULL":
                        j += 1
                        continue

                    if class_code in watched_departments[department]:
                        if class_code in found[department]:
                            found[department][class_code].append(class_code)
                        else:
                            found[department][class_code] = [class_code]
                        print(f"Matched CLASS CODE open: {class_code}")
                    else:
                        for course in watched_departments[department]:
                            is_course_number = not (course.isdigit() and len(course) == 5)
                            course_number_pattern = rf"{department.lower()}\s+{course.lower()}\s+"
                            matched_title = re.search(course_number_pattern, title_text)
                            if is_course_number and matched_title and class_type == "Lec":
                                if course in found[department]:
                                    found[department][course].append(class_code)
                                else:
                                    found[department][course] = [class_code]
                                print(f"Matched COURSE NUMBER open lecture: {department} {course} ({class_code})")
                    j += 1
            i += 1
    if found:
        notify_students(found)

    update_system_status()

    print(f"[PID {pid}] Finished check_courses task.")

if __name__ == "__main__":
    run_task()