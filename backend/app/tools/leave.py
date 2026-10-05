from typing import Annotated
from langgraph.prebuilt import InjectedState

from langchain_core.tools import tool

from app.db.supabase import supabase


@tool
def get_leave_balance(
    employee_id: Annotated[int, InjectedState("employee_id")]
) -> list[dict]:
    """
    Get the authenticated employee's leave balance for the current year.

    Use this tool when an employee asks about their available
    casual leave, earned leave, sick leave, or other leave balances.
    """
    response = (
        supabase
        .table("leave_balances")
        .select("leave_type, balance, year")
        .eq("employee_id", employee_id)
        .eq("year", 2026)
        .execute()
    )

    return response.data