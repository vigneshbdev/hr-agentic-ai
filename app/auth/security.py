import os 

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("JWT Secret not configured")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(
        password: str,
        password_hash: str
) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )

def create_access_token(employee_id: int) -> str:
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    )

    payload = {
        "sub": str(employee_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )

    return int(payload["sub"])