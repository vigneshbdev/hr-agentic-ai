from datetime import date

from langchain_core.tools import tool


@tool
def calculate_leave_days(
    start_date: str,
    end_date: str,
) -> dict:
    """
    Calculate the number of calendar days between a leave start date
    and end date, inclusive.

    Dates must be provided in YYYY-MM-DD format.

    Use this tool when an employee asks how many days a leave request
    would consume or wants to calculate the duration of a leave period.
    """

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return {
            "error": "Dates must use YYYY-MM-DD format."
        }

    if end < start:
        return {
            "error": "End date cannot be before start date."
        }

    days = (end - start).days + 1

    return {
        "start_date": start_date,
        "end_date": end_date,
        "leave_days": days,
    }