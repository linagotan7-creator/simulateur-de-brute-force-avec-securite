import time
import random
import string
import hashlib


class SecuritySystem:
    def __init__(self, max_attempts=5, lock_time=5):
        self.max_attempts = max_attempts
        self.lock_time = lock_time

        self._pin_hash = None
        self.attempts = 0
        self.locked_until = 0
        self.tested_codes = set()
        self.session_key = None

    # ================= PIN =================

    def set_pin(self, pin: str):
        self._pin_hash = self._hash(pin)
        self.attempts = 0
        self.tested_codes.clear()

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    # ================= LOCK =================

    def is_locked(self) -> bool:
        return time.time() < self.locked_until

    def _lock(self):
        self.locked_until = time.time() + self.lock_time
        self.attempts = 0

    # ================= SESSION =================

    def _new_session_key(self):
        self.session_key = ''.join(
            random.choices(string.ascii_letters + string.digits, k=16)
        )
        return self.session_key

    # ================= DEV MODE =================
    # Internal testing mode (triggered by GUI hash check)

    def enable_test_mode(self):
        self.attempts = 0
        self.locked_until = 0
        self.tested_codes.clear()

    # ================= TEST CODE =================

    def try_code(self, code: str, test_mode=False) -> str:
        if self.is_locked() and not test_mode:
            return "LOCKED"

        self.attempts += 1
        self.tested_codes.add(code)

        if self._hash(code) == self._pin_hash:
            self._new_session_key()
            return "SUCCESS"

        if self.attempts >= self.max_attempts and not test_mode:
            self._lock()
            return "LOCK"

        return "FAIL"

    # ================= BRUTE FORCE =================

    def next_code(self, test_mode=False):
        if test_mode:
            return f"{random.randint(0, 999):03d}"

        remaining = list(set(f"{i:03d}" for i in range(1000)) - self.tested_codes)
        if not remaining:
            return None
        return random.choice(remaining)
