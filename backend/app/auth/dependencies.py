from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.auth.security import decode_access_token
from app.db.supabase import supabase

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:

    token = credentials.credentials

    try:
        employee_id = decode_access_token(token)

        response = (
            supabase
            .table("employees")
            .select(
                "id, employee_code, name, email, role"
            )
            .eq("id", employee_id)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="Employee not found",
            )

        employee = response.data

        return {
            "employee_id": employee["id"],
            "role": employee["role"],
            "employee_code": employee["employee_code"],
            "name": employee["name"],
            "email": employee["email"],
        }

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


def require_hr_user(
    current_user: dict = Depends(get_current_user),
) -> dict:

    if current_user["role"] != "hr":
        raise HTTPException(
            status_code=403,
            detail="HR access required",
        )

    return current_user