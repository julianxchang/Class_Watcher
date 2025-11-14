from app.utils import create_chrome_driver, get_watched_department, notify_students
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import re, time, gc, os

def run():
    i = 0
    while True:
        print(f"Starting course check #{i+1}...")
        check_courses()
        i += 1
        time.sleep(120)

def check_courses():
    pid = os.getpid()
    print(f"[PID {pid}] Starting check_courses task...")
    driver = None
    found = {}
    watched_department = get_watched_department()

    for department in watched_department:
        try:
            driver = create_chrome_driver()

            driver.get("https://www.reg.uci.edu/perl/WebSoc")
            time.sleep(1)   # wait for page to load

            select = Select(driver.find_element("name", "Dept"))

            select.select_by_value(department)
            driver.find_element("name", "Submit").click()

            time.sleep(1)   # wait for page to load

            table = driver.find_element(By.CLASS_NAME, 'course-list').find_elements(By.TAG_NAME, "tr")
            i = 0
            tablelen = len(table)

            watched_courses = watched_department[department]
            print(f"Department: {department}")
            print(f"Watching courses: {watched_courses}")
            found = {}
            while (i < tablelen):
                try:
                    checkRow = table[i].find_element(By.CLASS_NAME, "CourseTitle")
                    text = checkRow.text.lower()
                    for course in watched_courses:
                        pattern = rf"{department.lower()}\s+{course.lower()}\s+"
                        if re.search(pattern, text):
                            print(f">>> Matched course: {department} {course}")
                            j = i + 1   # start searching to see if class if FULL from next row
                            while j < tablelen:
                                course_titles = table[j].find_elements(By.CLASS_NAME, "CourseTitle")
                                if course_titles:  # If list is not empty, we found the next course
                                    i = j - 1
                                    break

                                # This row doesn't have a CourseTitle, so it's a class section row
                                rows = table[j].find_elements(By.TAG_NAME, "td")
                                if rows:
                                    print([row.text for row in rows])
                                    if len(rows) > 10 and rows[1].text == "Lec" and rows[-1].text == "OPEN":
                                        classCode = rows[0].text
                                        print(f"Found open lecture: {classCode}")
                                        if course in found:
                                            found[course].append(classCode)
                                        else:
                                            found[course] = [classCode]
                                j += 1
                            break
                except Exception as exception:
                    pass
                finally:
                    i += 1
        except Exception as e:
            print(f"Error occurred during course check: {e}")
        finally:
            if driver:
                try:
                    driver.close()
                    driver.quit()
                except Exception as e:
                    print(f"Error occurred while quitting driver: {e}")
            gc.collect()
        if found:
            notify_students(found)

    print("Course check complete.")
    return True

if __name__ == "__main__":
    run()  # Runs 30 times with 10-second intervals (5 minutes total)
