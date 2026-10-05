from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.db.supabase import supabase


@tool
def validate_leave_request(
    leave_type: str,
    requested_days: int,
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> dict:
    """
    Validate whether the authenticated employee has enough balance
    for a requested number of days of a specific leave type.

    Use this tool when an employee asks whether they have enough
    leave balance for a specific leave type.
    """

    response = (
        supabase
        .table("leave_balances")
        .select("leave_type, balance, year")
        .eq("employee_id", employee_id)
        .eq("year", 2026)
        .execute()
    )

    balances = response.data

    if not balances:
        return {
            "valid": False,
            "reason": "No leave balances found for this employee.",
        }

    requested_type = leave_type.strip().lower()

    matching_balance = next(
        (
            row
            for row in balances
            if row["leave_type"].strip().lower() == requested_type
        ),
        None,
    )

    if not matching_balance:
        return {
            "valid": False,
            "reason": f"No {leave_type} balance found for 2026.",
            "available_leave_types": [
                row["leave_type"] for row in balances
            ],
        }

    balance = float(matching_balance["balance"])

    return {
        "valid": balance >= requested_days,
        "leave_type": matching_balance["leave_type"],
        "available_balance": balance,
        "requested_days": requested_days,
        "remaining_balance": balance - requested_days,
    }