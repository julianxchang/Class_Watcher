from . import run

@run.task()
def run_program(email, courseNumber, runTime):
    import multiprocessing as mp
    p = mp.Process(target=script, args=(email, courseNumber, runTime))
    p.start()
    p.join()

#@run.task()
def script(email, courseNumber, runTime):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    import time

    run_time_sec = int(runTime) * 60 # calculate number of seconds in given minutes

    start_time = time.time()
    stop_time = start_time + run_time_sec

    send_confirmation_email(email, courseNumber, int(runTime))

    runs = 0 # each run is 2 minutes

    while(time.time() < stop_time):
        #send check email every 30 minutes
        if (runs % 15 == 0):
            check_email(email, courseNumber, int(runTime), int(stop_time))

        print(courseNumber)

        driver = create_chrome_driver()

        # go to UCI Webreg
        driver.get("https://www.reg.uci.edu/perl/WebSoc")

        # Find dropdown menu
        select = Select(driver.find_element("name", "Dept"))

        # NEED TO UPDATE CODE SO YOU CAN CHOOSE WHICH SCHOOL
        select.select_by_value("I&C SCI")
        driver.find_element("name", "Submit").click()

        table = driver.find_elements(By.XPATH, ".//div[@class='course-list']/table/tbody/tr")
        i = 0
        found = False

        while (i < len(table) and found == False):
            try:
                checkRow = table[i].find_element(By.CLASS_NAME, "CourseTitle")
                text = checkRow.text
                print(text)
                if "I&C Sci" in text and " " + courseNumber + " " in text:
                    j = i + 1
                    while(True): # need to update to stop when (currently uses exception to check)
                        try:
                            checkCourseTitle = table[j].find_element(By.CLASS_NAME, "CourseTitle")
                            break # if course title exists it means we've reached the next course, therefore break out of while loop
                        except Exception as e: # getting error here means we still haven't reached next course
                            print(e)
                            try:
                                rows = table[j].find_elements(By.TAG_NAME, "td")
                                j += 1
                                print(rows[1].text)
                                if rows[1].text == "Lec" and rows[-1].text == "OPEN":
                                    classCode = rows[0].text
                                    send_email(classCode, courseNumber, email)
                                found = True
                            except Exception as e:
                                print(e)
            except Exception as exception:
                print(exception)
                #pass
            finally:
                i += 1
        driver.close()
        driver.quit()
        time.sleep(120) # wait 10 minutes before checking website again
        runs += 1
    complete_email(email, courseNumber, int(runTime))
    return None


def create_chrome_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    return driver


def complete_email(email, courseNumber, duration):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os
    import time

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"
    receiver_email = "uciclasswatcher@gmail.com"

    load_dotenv()
    password = os.getenv("password")


    msg = EmailMessage()
    msg['Subject'] = f"{email} finished watching {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"{email} finished watching ICS {courseNumber}.\nWatch duration: {duration} minute(s)")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")


def check_email(email, courseNumber, duration, stopTime):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os
    import time

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"
    receiver_email = "uciclasswatcher@gmail.com"

    load_dotenv()
    password = os.getenv("password")


    msg = EmailMessage()
    msg['Subject'] = f"{email} is watching ICS {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"{email} is watching ICS {courseNumber} as of {get_time()}\nWatch duration: {duration} minute(s)\nRemaining time: {int((stopTime-int(time.time()))/60)} minute(s)")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")


def get_time(): # New York Timezone
    from datetime import datetime
    import pytz

    new_york_tz = pytz.timezone('America/New_York')
    current_time = datetime.now(new_york_tz).strftime('%Y-%m-%d %I:%M:%S %p')

    return current_time


def send_confirmation_email(email, courseNumber, duration):
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
    msg.set_content(f"You will be notified when a spot opens up.\nWatch duration: {duration} minute(s)")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")


def send_email(classCode, courseNumber, email):
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
    msg.set_content(f"SPOT OPEN IN ICS {courseNumber} AS OF {get_time()}\nClass code: {classCode}\nDon't forget to enroll in all coclasses!")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")