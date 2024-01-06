from . import run

@run.task()
def run_program(email, courseNumber, run_time):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    import time

    run_time = int(run_time) * 60 # calculate number of seconds in given minutes

    current_time = time.time()
    stop_time = current_time + run_time

    send_confirmation_email(courseNumber, email)

    while(time.time() < stop_time):
        print(courseNumber)
        # Create a new instance of the Chrome driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # go to UCI Webreg
        driver.get("https://www.reg.uci.edu/perl/WebSoc")

        # Find dropdown menu
        select = Select(driver.find_element("name", "Dept"))

        # NEED TO UPDATE CODE SO YOU CAN CHOOSE WHICH SCHOOL
        #select.select_by_index(71)
        select.select_by_value("I&C SCI")
        btn = driver.find_element("name", "Submit").click()

        table = driver.find_elements(By.XPATH, ".//div[@class='course-list']/table/tbody/tr")
        i = 0
        found = False

        while (i < len(table) and found == False):
            try:
                checkRow = table[i].find_element(By.CLASS_NAME, "CourseTitle")
                text = checkRow.text
                print(text)
                if "I&C Sci" in text and courseNumber in text:
                    j = i + 1
                    while(True):
                        try:
                            checkCourseTitle = table[j].find_element(By.CLASS_NAME, "CourseTitle")
                            break
                        except Exception as e: # getting error here means we still haven't reached next course
                            print(e)
                            try:
                                rows = table[j].find_elements(By.TAG_NAME, "td")
                                j += 1
                                print(rows[1].text)
                                if rows[1].text == "Lec" and rows[-1].text != "FULL":
                                    classCode = rows[0].text
                                    try:
                                        send_email(classCode, courseNumber, email)
                                    except Exception as e:
                                        print(e)
                                found = True
                            except Exception as e:
                                print(e)

            except Exception as exception:
                print(exception)
                #pass
            finally:
                i += 1
        time.sleep(120) # wait 10 minutes before checking website again
        driver.quit()
    return None


def get_time(): # New York Timezone
    from datetime import datetime
    import pytz

    new_york_tz = pytz.timezone('America/New_York')
    current_time = datetime.now(new_york_tz).strftime('%Y-%m-%d %I:%M:%S %p')

    return current_time


def send_confirmation_email(courseNumber, email):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"  # Enter your address
    receiver_email = email  # Enter receiver address

    load_dotenv()
    password = os.getenv("password")


    msg = EmailMessage()
    msg['Subject'] = f"Successfully started watching ICS {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"You will be notified when a spot opens up.")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")


def send_email(courseNumber, email):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os


    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"  # Enter your address
    receiver_email = email  # Enter receiver address

    load_dotenv()
    password = os.getenv("password")


    msg = EmailMessage()
    msg['Subject'] = f"SPOT OPEN IN ICS {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"SPOT OPEN IN ICS {courseNumber} AS OF {get_time()} \nClass code: {classCode}")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")