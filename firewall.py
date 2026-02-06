import time
import json
import os

DATA_DIR = "data"
LOCK_FILE = os.path.join(DATA_DIR, "lock.json")

MAX_ATTEMPTS = 5
LOCK_DURATION = 30


def _load():
    if not os.path.exists(LOCK_FILE):
        return {"fails": 0, "locked_until": 0}
    with open(LOCK_FILE, "r") as f:
        return json.load(f)


def _save(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        json.dump(data, f)


def is_locked():
    data = _load()
    return time.time() < data["locked_until"]


def remaining_time():
    data = _load()
    return max(0, int(data["locked_until"] - time.time()))


def register_fail():
    data = _load()
    data["fails"] += 1

    if data["fails"] >= MAX_ATTEMPTS:
        data["locked_until"] = time.time() + LOCK_DURATION
        data["fails"] = 0

    _save(data)


def reset_after_success():
    _save({"fails": 0, "locked_until": 0})
