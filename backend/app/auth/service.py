from app.auth.security import (
    create_access_token,
    verify_password,
)
from app.db.supabase import supabase


def authenticate_employee(
    email: str,
    password: str,
) -> str | None:

    response = (
        supabase
        .table("employees")
        .select("id, email, password_hash, role")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    employee = response.data[0]

    password_hash = employee.get("password_hash")

    if not password_hash:
        return None

    if not verify_password(password, password_hash):
        return None

    return create_access_token(
        employee["id"],
        employee["role"],
    )