import time
import subprocess

def run_requests():
    i = 0
    while True:
        print(f"Starting course check #{i+1}...")
        subprocess.run(["python3", "worker.py"])
        i += 1
        time.sleep(120)  # check every 2 minutes

if __name__ == "__main__":
    run_requests()