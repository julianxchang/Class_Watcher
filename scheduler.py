import time
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def run_requests():
    i = 0
    while True:
        print(f"Starting course check #{i+1}...")
        subprocess.run(["python3", "worker.py"])
        i += 1
        if os.getenv('ENV') == 'prod':
            time.sleep(300)  # check every 5 minutes
        elif os.getenv('ENV') == 'dev':
            time.sleep(10)  # check every 10 seconds

if __name__ == "__main__":
    run_requests()