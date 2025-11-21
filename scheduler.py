import time
import subprocess
import os
from dotenv import load_dotenv
import sys

load_dotenv()

def run_requests():
    i = 0
    while True:
        print(f"Starting course check #{i+1}...")
        subprocess.run([sys.executable, "worker.py"])
        i += 1
        if os.getenv('ENV') == 'prod':
            time.sleep(120)  # check every 2 minutes
        elif os.getenv('ENV') == 'dev':
            time.sleep(10)  # check every 10 seconds

if __name__ == "__main__":
    run_requests()