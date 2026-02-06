import os
from datetime import datetime

LOG_FILE = "data/attempts.txt"


def log(ip, code, status):
    os.makedirs("data", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {ip} | {code} | {status}\n")
