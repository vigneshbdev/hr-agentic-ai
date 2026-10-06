from datetime import date
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.db.supabase import supabase

@tool
def get_leave_requests(
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> list[dict]:
    """
    Get the authenticated employee's leave requests.

    Use this tool when the employee asks about:
    - their leave request history
    - submitted leave requests
    - pending leave requests
    - approved or rejected leave requests
    - the status of a leave request

    Never use this tool to retrieve another employee's requests.
    """

    response = (
        supabase
        .table("leave_requests")
        .select(
            "id, leave_type, start_date, end_date, status, created_at"
        )
        .eq("employee_id", employee_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

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

@tool
def get_pending_leave_requests(
    role: Annotated[str, InjectedState("role")],
) -> list[dict]:
    """
    Get all pending leave requests for HR review.

    This tool is restricted to HR users.
    Use it when an HR user asks to see pending,
    awaiting approval, or unprocessed leave requests.
    """

    if role != "hr":
        return {
            "error": "Unauthorized. HR access is required."
        }

    response = (
        supabase
        .table("leave_requests")
        .select(
            "id, employee_id, leave_type, "
            "start_date, end_date, status, created_at"
        )
        .eq("status", "Pending")
        .order("created_at", desc=True)
        .execute()
    )

    requests = response.data or []

    if not requests:
        return {
            "message": "There are no pending leave requests."
        }

    employee_ids = list({
        request["employee_id"]
        for request in requests
    })

    employees_response = (
        supabase
        .table("employees")
        .select(
            "id, employee_code, name, email, department"
        )
        .in_("id", employee_ids)
        .execute()
    )

    employees = {
        employee["id"]: employee
        for employee in (employees_response.data or [])
    }

    result = []

    for request in requests:
        employee = employees.get(request["employee_id"], {})

        result.append({
            "request_id": request["id"],
            "employee_id": request["employee_id"],
            "employee_code": employee.get("employee_code"),
            "employee_name": employee.get("name"),
            "department": employee.get("department"),
            "leave_type": request["leave_type"],
            "start_date": request["start_date"],
            "end_date": request["end_date"],
            "status": request["status"],
            "created_at": request["created_at"],
        })

    return result

@tool
def approve_leave_request(
    request_id: int,
    role: Annotated[str, InjectedState("role")],
) -> dict:
    """
    Approve a pending employee leave request.

    This tool is restricted to HR users.
    Use only when an HR user explicitly asks to approve
    a specific leave request.
    """

    if role != "hr":
        return {
            "success": False,
            "error": "Unauthorized. HR access is required.",
        }

    # Check that the request exists
    response = (
        supabase
        .table("leave_requests")
        .select(
            "id, employee_id, leave_type, "
            "start_date, end_date, status"
        )
        .eq("id", request_id)
        .single()
        .execute()
    )

    request = response.data

    if not request:
        return {
            "success": False,
            "error": f"Leave request {request_id} was not found.",
        }

    # Prevent approving an already processed request
    if request["status"] != "Pending":
        return {
            "success": False,
            "error": (
                f"Leave request {request_id} is already "
                f"{request['status']}."
            ),
        }

    # Approve the request
    update_response = (
        supabase
        .table("leave_requests")
        .update({"status": "Approved"})
        .eq("id", request_id)
        .eq("status", "Pending")
        .execute()
    )

    if not update_response.data:
        return {
            "success": False,
            "error": "Unable to approve the leave request.",
        }

    return {
        "success": True,
        "request_id": request_id,
        "employee_id": request["employee_id"],
        "leave_type": request["leave_type"],
        "start_date": request["start_date"],
        "end_date": request["end_date"],
        "status": "Approved",
    }


@tool
def reject_leave_request(
    request_id: int,
    reason: str,
    role: Annotated[str, InjectedState("role")],
) -> dict:
    """
    Reject a pending employee leave request.

    This tool is restricted to HR users.
    Use only when an HR user explicitly asks to reject
    a specific leave request.
    A rejection reason is required.
    """

    if role != "hr":
        return {
            "success": False,
            "error": "Unauthorized. HR access is required.",
        }

    if not reason.strip():
        return {
            "success": False,
            "error": "A rejection reason is required.",
        }

    response = (
        supabase
        .table("leave_requests")
        .select(
            "id, employee_id, leave_type, "
            "start_date, end_date, status"
        )
        .eq("id", request_id)
        .single()
        .execute()
    )

    request = response.data

    if not request:
        return {
            "success": False,
            "error": f"Leave request {request_id} was not found.",
        }

    if request["status"] != "Pending":
        return {
            "success": False,
            "error": (
                f"Leave request {request_id} is already "
                f"{request['status']}."
            ),
        }

    update_response = (
        supabase
        .table("leave_requests")
        .update({
            "status": "Rejected",
        })
        .eq("id", request_id)
        .eq("status", "Pending")
        .execute()
    )

    if not update_response.data:
        return {
            "success": False,
            "error": "Unable to reject the leave request.",
        }

    return {
        "success": True,
        "request_id": request_id,
        "employee_id": request["employee_id"],
        "leave_type": request["leave_type"],
        "start_date": request["start_date"],
        "end_date": request["end_date"],
        "status": "Rejected",
        "reason": reason,
    }