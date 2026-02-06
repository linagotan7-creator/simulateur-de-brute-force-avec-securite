import base64


def encrypt(data: str, key: str) -> str:
    combined = key + "::" + data
    return base64.b64encode(combined.encode()).decode()


def decrypt(token: str, key: str):
    try:
        decoded = base64.b64decode(token.encode()).decode()
        k, data = decoded.split("::", 1)
        if k == key:
            return data
    except Exception:
        pass
    return None
