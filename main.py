import os
import random
import time

from firewall import (
    is_locked,
    remaining_time,
    register_fail,
    reset_after_success
)

from logger import log
from utils import fake_ip

# =========================
# CONFIGURATION
# =========================

TEST_MODE = False

DATA_DIR = "data"
CODE_FILE = os.path.join(DATA_DIR, "code.sys")
SECRET_FILE = os.path.join(DATA_DIR, "secret.txt")
LOCKED_FILE = os.path.join(DATA_DIR, "secret.txt.lock")
ATTEMPTS_FILE = os.path.join(DATA_DIR, "attempts.mem")

MAX_ATTEMPTS_BEFORE_LOCK = 10
DELAY_BETWEEN_ATTEMPTS = 0.5


# =========================
# MODE TEST
# =========================

def enable_test_mode():
    global TEST_MODE
    TEST_MODE = True


def disable_test_mode():
    global TEST_MODE
    TEST_MODE = False


# =========================
# UTILITAIRES
# =========================

def load_attempted_codes():
    if not os.path.exists(ATTEMPTS_FILE):
        return set()
    with open(ATTEMPTS_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_attempted_code(code):
    with open(ATTEMPTS_FILE, "a") as f:
        f.write(code + "\n")


def reset_attempts_memory():
    if os.path.exists(ATTEMPTS_FILE):
        os.remove(ATTEMPTS_FILE)


# =========================
# LOGIQUE PRINCIPALE
# =========================

def save_code(code: str):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(CODE_FILE, "w") as f:
        f.write(code)

    reset_attempts_memory()

    if not os.path.exists(SECRET_FILE) and not os.path.exists(LOCKED_FILE):
        with open(SECRET_FILE, "w") as f:
            f.write("Fichier secret protégé 🔐")

    if os.path.exists(SECRET_FILE):
        os.rename(SECRET_FILE, LOCKED_FILE)


def brute_force(log_callback):
    if not TEST_MODE and is_locked():
        log_callback(f"⛔ Système verrouillé ({remaining_time()}s restantes)")
        return

    if not os.path.exists(CODE_FILE):
        log_callback("❌ Aucun code enregistré")
        return

    with open(CODE_FILE, "r") as f:
        real_code = f.read().strip()

    attempted = load_attempted_codes()
    all_codes = {str(i).zfill(3) for i in range(1000)}
    remaining_codes = list(all_codes - attempted)

    if not remaining_codes:
        log_callback("⚠️ Tous les codes ont déjà été testés")
        return

    log_callback(
        f"🚀 Démarrage brute force "
        f"({'MODE TEST' if TEST_MODE else 'MODE NORMAL'})"
    )

    ip = fake_ip()
    attempts_counter = 0

    while remaining_codes:
        attempt = random.choice(remaining_codes)
        remaining_codes.remove(attempt)

        log_callback(f"🔎 Tentative depuis {ip} : {attempt}")
        log(ip, attempt, "TRY")
        save_attempted_code(attempt)

        if attempt == real_code:
            reset_after_success()
            reset_attempts_memory()

            if os.path.exists(LOCKED_FILE):
                os.rename(LOCKED_FILE, SECRET_FILE)

            log(ip, attempt, "SUCCESS")
            log_callback("✅ Code trouvé ! Fichier déverrouillé 🔓")
            return

        attempts_counter += 1
        log(ip, attempt, "FAIL")

        if not TEST_MODE:
            register_fail()
            time.sleep(DELAY_BETWEEN_ATTEMPTS)

        if not TEST_MODE and attempts_counter >= MAX_ATTEMPTS_BEFORE_LOCK:
            log_callback("⛔ Trop de tentatives — verrouillage temporaire")
            return

    log_callback("❌ Code introuvable")
