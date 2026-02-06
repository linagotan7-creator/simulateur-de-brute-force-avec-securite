import random
import os


def fake_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def hide_file(path):
    os.system(f'attrib +h "{path}"')
