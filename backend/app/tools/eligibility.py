from datetime import date

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Annotated

from app.db.supabase import supabase


@tool
def check_leave_eligibility(
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> dict:
    """
    Check whether the authenticated employee is eligible for annual leave.

    Use this tool when an employee asks whether they are eligible
    to take annual leave or wants to know their leave eligibility status.
    """

    response = (
        supabase
        .table("employees")
        .select("joining_date")
        .eq("id", employee_id)
        .single()
        .execute()
    )

    employee = response.data

    if not employee:
        return {
            "eligible": False,
            "reason": "Employee profile not found",
        }

    joining_date = date.fromisoformat(employee["joining_date"])
    today = date.today()

    days_employed = (today - joining_date).days

    eligible = days_employed >= 30

    return {
        "eligible": eligible,
        "joining_date": employee["joining_date"],
        "days_employed": days_employed,
        "minimum_days_required": 30,
    }