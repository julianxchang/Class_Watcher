from app.huey import run, crontab
from app.utils import create_chrome_driver, get_watched_courses, notify_students
import time

@run.periodic_task(crontab(minute='*/2'))   # run every 10 minutes
def check_courses():
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    import re

    driver = create_chrome_driver()

    driver.get("https://www.reg.uci.edu/perl/WebSoc")

    time.sleep(2)  # wait for page to load

    select = Select(driver.find_element("name", "Dept"))

    # TODO: Make it so user can select department other than ICS
    select.select_by_value("I&C SCI")
    driver.find_element("name", "Submit").click()

    table = driver.find_element(By.CLASS_NAME, 'course-list').find_elements(By.TAG_NAME, "tr")
    i = 0
    tablelen = len(table)

    watched_courses = get_watched_courses()

    print(f"Watching courses: {watched_courses}")

    found = {}
    while (i < tablelen):
        try:
            checkRow = table[i].find_element(By.CLASS_NAME, "CourseTitle")
            text = checkRow.text
            for num in watched_courses:
                pattern = rf"I&C Sci\s+{num}\s+"
                if re.search(pattern, text):
                    print(f">>> Matched course: I&C Sci {num}")
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
                                found[num].append(classCode) if num in found else found.update({num: [classCode]})
                                # send_email(classCode, 33, email)  # You'll need to define email variable
                        j += 1
                    break
        except Exception as exception:
            pass
        finally:
            i += 1
    driver.close()
    driver.quit()
    if found:
        notify_students(found)