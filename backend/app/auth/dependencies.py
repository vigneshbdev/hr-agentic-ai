from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.auth.security import decode_access_token

security = HTTPBearer()


def get_current_employee(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials

    try:
        employee_id = decode_access_token(token)
        return employee_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="JWT token has expired",
        )

    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=401,
            detail="JWT signature is invalid",
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid JWT: {str(e)}",
        )