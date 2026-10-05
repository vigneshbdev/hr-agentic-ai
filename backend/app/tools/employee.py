from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.db.supabase import supabase

@tool
def get_employee_profile(
    employee_id : Annotated[int, InjectedState("employee_id")]
) -> dict:
    """
    Get the authenticated employee's current-year leave balances.
    Use for questions about available leave balance.
    """

    response = (
        supabase.table('employees').select('employee_code, name, email, department, joining_date').eq('id', employee_id).single().execute()
    )

    if not response.data:
        return {"error": "Employee Profile Not Found"}

    return response.data