from datetime import date
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.db.supabase import supabase


@tool
def submit_leave_request(
    leave_type: str,
    start_date: str,
    end_date: str,
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> dict:
    """
    Submit a leave request for the authenticated employee.

    IMPORTANT:
    Only use this tool when the employee explicitly asks to submit,
    apply for, or proceed with a leave request.

    Do not submit a request merely because the employee asks whether
    they are eligible or whether they have enough leave balance.

    Dates must use YYYY-MM-DD format.
    """

    # Validate dates
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return {
            "success": False,
            "error": "Dates must use YYYY-MM-DD format.",
        }

    if end < start:
        return {
            "success": False,
            "error": "End date cannot be before start date.",
        }

    requested_days = (end - start).days + 1

    # Check leave balance
    balance_response = (
        supabase
        .table("leave_balances")
        .select("leave_type, balance, year")
        .eq("employee_id", employee_id)
        .eq("year", 2026)
        .execute()
    )

    balances = balance_response.data

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
            "success": False,
            "error": f"No {leave_type} balance found for 2026.",
            "available_leave_types": [
                row["leave_type"] for row in balances
            ],
        }

    available_balance = float(matching_balance["balance"])

    if available_balance < requested_days:
        return {
            "success": False,
            "error": "Insufficient leave balance.",
            "leave_type": matching_balance["leave_type"],
            "available_balance": available_balance,
            "requested_days": requested_days,
        }

    # Submit request
    response = (
        supabase
        .table("leave_requests")
        .insert({
            "employee_id": employee_id,
            "leave_type": matching_balance["leave_type"],
            "start_date": start_date,
            "end_date": end_date,
            "status": "Pending",
        })
        .execute()
    )

    if not response.data:
        return {
            "success": False,
            "error": "Unable to create leave request.",
        }

    request = response.data[0]

    return {
        "success": True,
        "request_id": request["id"],
        "leave_type": matching_balance["leave_type"],
        "start_date": start_date,
        "end_date": end_date,
        "requested_days": requested_days,
        "status": "Pending",
        "remaining_balance": available_balance - requested_days,
    }