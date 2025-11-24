import time, subprocess, os, sys, requests
from dotenv import load_dotenv

from app.db import get_db_conn, release_db_conn

load_dotenv()

HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")

def run_requests():
    i = 0
    while True:
        print(f"Starting course check #{i+1}...")
        subprocess.run([sys.executable, "worker.py"])

        # send heartbeat
        try:
            requests.get(HEARTBEAT_URL, timeout=5)
            print("Heartbeat sent.")
        except Exception as e:
            print("Failed to send heartbeat:", e)

        # update last scraped time in db
        try:
            conn = get_db_conn()
            cur = conn.cursor()
            cur.execute("UPDATE system_status SET last_scrape = NOW() WHERE id = 1;")
            conn.commit()
            release_db_conn(conn)
            print("Updated last scrape time in database.")
        except Exception as e:
            print("Failed to update last scrape time:", e)

        i += 1
        if os.getenv('ENV') == 'prod':
            time.sleep(120)  # check every 2 minutes
        elif os.getenv('ENV') == 'dev':
            time.sleep(10)  # check every 10 seconds

if __name__ == "__main__":
    run_requests()