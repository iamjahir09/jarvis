import os
import sys
import subprocess
from time import sleep

DJANGO_DIR = "C:\\Users\\pc\\Desktop\\assis\\automotive_ai"

while True:
    try:
        # Django server start karo
        os.chdir(DJANGO_DIR)
        subprocess.Popen(["python", "manage.py", "runserver"])
        sleep(5)  # Thoda wait karo
    except Exception as e:
        print(f"Error: {e}")
        sleep(10)  # Agar crash hua toh 10 second wait karo