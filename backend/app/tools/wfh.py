from datetime import date, timedelta
from typing import Annotated
import re

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.db.supabase import supabase
from app.rag.embeddings import generate_embedding

from app.rag.repository import search_policy


# ============================================================
# WFH POLICY
# ============================================================

def get_wfh_policy_limits() -> dict:
    """
    Retrieve WFH limits from the HR policy using RAG.

    The WFH policy document is the source of truth for:
    - Maximum WFH days per week
    - Maximum WFH days per month

    The actual employee usage is retrieved separately from
    the wfh_requests table.
    """

    query = """
    WFH work from home policy:
    maximum WFH days per week,
    maximum WFH days per month,
    weekly WFH limit,
    monthly WFH limit
    """

    # Generate embedding using the same embedding model
    # used during policy ingestion.
    query_embedding = generate_embedding(query)

    # Search the existing policy_documents vector store.
    policy_results = search_policy(
        query_embedding=query_embedding,
        match_count=5,
    )
    if not policy_results:
        raise ValueError(
            "Unable to retrieve the WFH policy from the policy knowledge base."
        )

    policy_text = " ".join(
        " ".join(str(item).split())
        for result in policy_results
        for item in (
            result["content"]
            if isinstance(result["content"], list)
            else [result["content"]]
        )
    )

    print("\n--- NORMALIZED POLICY TEXT ---")
    print(policy_text)

    # --------------------------------------------------------
    # Extract weekly limit
    # --------------------------------------------------------

    weekly_patterns = [
        r"(\d+)\s+WFH\s+days?\s+per\s+week",
        r"maximum\s+of\s+(\d+)\s+WFH\s+days?\s+per\s+week",
        r"up\s+to\s+(\d+)\s+days?\s+per\s+week",
        r"(\d+)\s+days?\s+per\s+week",
        r"(\d+)\s+WFH\s+days?\s*/\s*week",
        r"(\d+)\s+days?\s*/\s*week",
    ]

    weekly_limit = None

    for pattern in weekly_patterns:
        match = re.search(
            pattern,
            policy_text,
            flags=re.IGNORECASE,
        )

        if match:
            weekly_limit = int(match.group(1))
            break

    # --------------------------------------------------------
    # Extract monthly limit
    # --------------------------------------------------------

    monthly_patterns = [
        r"up\s+to\s+a\s+maximum\s+of\s+(\d+)\s+days?\s+in\s+a\s+month",
        r"maximum\s+of\s+(\d+)\s+days?\s+in\s+a\s+month",
        r"(\d+)\s+days?\s+in\s+a\s+month",
        r"(\d+)\s+WFH\s+days?\s+per\s+month",
        r"up\s+to\s+(\d+)\s+days?\s+per\s+month",
        r"maximum\s+(\d+)\s+days?\s+per\s+month",
    ]

    monthly_limit = None

    for pattern in monthly_patterns:
        match = re.search(
            pattern,
            policy_text,
            flags=re.IGNORECASE,
        )

        if match:
            monthly_limit = int(match.group(1))
            break

    # --------------------------------------------------------
    # Validate policy extraction
    # --------------------------------------------------------

    if weekly_limit is None:
        raise ValueError(
            "Unable to determine the weekly WFH limit from the HR policy."
        )

    if monthly_limit is None:
        raise ValueError(
            "Unable to determine the monthly WFH limit from the HR policy."
        )

    return {
        "weekly_limit": weekly_limit,
        "monthly_limit": monthly_limit,
        "policy_documents": list(
            {
                result.get("document_name")
                for result in policy_results
                if result.get("document_name")
            }
        ),
        "policy_text": policy_text,
    }


# ============================================================
# GET MONTHLY WFH USAGE
# ============================================================

@tool
def get_wfh_usage(
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> dict:
    """
    Get the authenticated employee's WFH usage for the current month.

    The WFH limits are retrieved dynamically from the HR policy
    through RAG.

    Use this tool when an employee asks:
    - How many WFH days have I used?
    - How many WFH days do I have remaining?
    - What is my WFH usage this month?
    """

    try:
        policy = get_wfh_policy_limits()
    except ValueError as exc:
        return {
            "error": str(exc),
        }

    monthly_limit = policy["monthly_limit"]

    today = date.today()

    month_start = today.replace(day=1)

    if today.month == 12:
        next_month = today.replace(
            year=today.year + 1,
            month=1,
            day=1,
        )
    else:
        next_month = today.replace(
            month=today.month + 1,
            day=1,
        )

    response = (
        supabase
        .table("wfh_requests")
        .select("id, wfh_date, status")
        .eq("employee_id", employee_id)
        .gte("wfh_date", month_start.isoformat())
        .lt("wfh_date", next_month.isoformat())
        .eq("status", "Approved")
        .order("wfh_date")
        .execute()
    )

    records = response.data or []

    used_days = len(records)

    remaining_days = max(
        monthly_limit - used_days,
        0,
    )

    return {
        "employee_id": employee_id,
        "year": today.year,
        "month": today.month,
        "used_wfh_days": used_days,
        "monthly_limit": monthly_limit,
        "remaining_wfh_days": remaining_days,
        "wfh_dates": [
            record["wfh_date"]
            for record in records
        ],
        "policy_source": policy["policy_documents"],
    }


# ============================================================
# GET WEEKLY WFH USAGE
# ============================================================

@tool
def get_wfh_weekly_usage(
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> dict:
    """
    Get the authenticated employee's WFH usage for the current week.

    The week is calculated from Monday through Sunday.

    The weekly WFH limit is retrieved dynamically from the HR
    policy through RAG.
    """

    try:
        policy = get_wfh_policy_limits()
    except ValueError as exc:
        return {
            "error": str(exc),
        }

    weekly_limit = policy["weekly_limit"]

    today = date.today()

    week_start = today - timedelta(
        days=today.weekday()
    )

    week_end = week_start + timedelta(days=6)

    response = (
        supabase
        .table("wfh_requests")
        .select("id, wfh_date, status")
        .eq("employee_id", employee_id)
        .eq("status", "Approved")
        .gte("wfh_date", week_start.isoformat())
        .lte("wfh_date", week_end.isoformat())
        .order("wfh_date")
        .execute()
    )

    records = response.data or []

    used_days = len(records)

    remaining_days = max(
        weekly_limit - used_days,
        0,
    )

    return {
        "employee_id": employee_id,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "used_wfh_days": used_days,
        "weekly_limit": weekly_limit,
        "remaining_wfh_days": remaining_days,
        "wfh_dates": [
            record["wfh_date"]
            for record in records
        ],
        "policy_source": policy["policy_documents"],
    }


# ============================================================
# CHECK WFH ELIGIBILITY
# ============================================================

@tool
def check_wfh_eligibility(
    requested_date: str,
    employee_id: Annotated[int, InjectedState("employee_id")],
) -> dict:
    """
    Check whether the authenticated employee can take WFH
    on a requested date.

    WFH policy limits are retrieved dynamically through RAG.

    Actual employee WFH usage is retrieved from Supabase.

    The final eligibility calculation is deterministic.
    """

    # --------------------------------------------------------
    # Validate requested date
    # --------------------------------------------------------

    try:
        requested = date.fromisoformat(requested_date)
    except ValueError:
        return {
            "eligible": False,
            "error": "Date must use YYYY-MM-DD format.",
        }

    # --------------------------------------------------------
    # Retrieve policy through RAG
    # --------------------------------------------------------

    try:
        policy = get_wfh_policy_limits()
    except ValueError as exc:
        return {
            "eligible": False,
            "error": str(exc),
        }

    weekly_limit = policy["weekly_limit"]
    monthly_limit = policy["monthly_limit"]

    # --------------------------------------------------------
    # Monthly usage
    # --------------------------------------------------------

    month_start = requested.replace(day=1)

    if requested.month == 12:
        next_month = requested.replace(
            year=requested.year + 1,
            month=1,
            day=1,
        )
    else:
        next_month = requested.replace(
            month=requested.month + 1,
            day=1,
        )

    month_response = (
        supabase
        .table("wfh_requests")
        .select("id, wfh_date")
        .eq("employee_id", employee_id)
        .eq("status", "Approved")
        .gte("wfh_date", month_start.isoformat())
        .lt("wfh_date", next_month.isoformat())
        .execute()
    )

    monthly_records = month_response.data or []

    monthly_used = len(monthly_records)

    monthly_remaining = max(
        monthly_limit - monthly_used,
        0,
    )

    # --------------------------------------------------------
    # Weekly usage
    # Monday = 0
    # Sunday = 6
    # --------------------------------------------------------

    week_start = requested - timedelta(
        days=requested.weekday()
    )

    week_end = week_start + timedelta(days=6)

    week_response = (
        supabase
        .table("wfh_requests")
        .select("id, wfh_date")
        .eq("employee_id", employee_id)
        .eq("status", "Approved")
        .gte("wfh_date", week_start.isoformat())
        .lte("wfh_date", week_end.isoformat())
        .execute()
    )

    weekly_records = week_response.data or []

    weekly_used = len(weekly_records)

    weekly_remaining = max(
        weekly_limit - weekly_used,
        0,
    )

    # --------------------------------------------------------
    # Already scheduled?
    # --------------------------------------------------------

    already_exists = any(
        record["wfh_date"] == requested_date
        for record in monthly_records
    )

    if already_exists:
        return {
            "eligible": False,
            "reason": "WFH is already recorded for this date.",
            "requested_date": requested_date,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "weekly_used": weekly_used,
            "weekly_limit": weekly_limit,
            "weekly_remaining": weekly_remaining,
            "monthly_used": monthly_used,
            "monthly_limit": monthly_limit,
            "monthly_remaining": monthly_remaining,
            "policy_source": policy["policy_documents"],
        }

    # --------------------------------------------------------
    # Weekly limit validation
    # --------------------------------------------------------

    if weekly_used >= weekly_limit:
        return {
            "eligible": False,
            "reason": (
                f"Weekly WFH limit of {weekly_limit} days "
                "has already been reached."
            ),
            "requested_date": requested_date,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "weekly_used": weekly_used,
            "weekly_limit": weekly_limit,
            "weekly_remaining": weekly_remaining,
            "monthly_used": monthly_used,
            "monthly_limit": monthly_limit,
            "monthly_remaining": monthly_remaining,
            "policy_source": policy["policy_documents"],
        }

    # --------------------------------------------------------
    # Monthly limit validation
    # --------------------------------------------------------

    if monthly_used >= monthly_limit:
        return {
            "eligible": False,
            "reason": (
                f"Monthly WFH limit of {monthly_limit} days "
                "has already been reached."
            ),
            "requested_date": requested_date,
            "monthly_used": monthly_used,
            "monthly_limit": monthly_limit,
            "monthly_remaining": monthly_remaining,
            "weekly_used": weekly_used,
            "weekly_limit": weekly_limit,
            "weekly_remaining": weekly_remaining,
            "policy_source": policy["policy_documents"],
        }

    # --------------------------------------------------------
    # Eligible
    # --------------------------------------------------------

    return {
        "eligible": True,
        "reason": (
            "WFH is within the weekly and monthly limits "
            "defined in the HR policy."
        ),
        "requested_date": requested_date,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "weekly_used": weekly_used,
        "weekly_limit": weekly_limit,
        "weekly_remaining_before_request": weekly_remaining,
        "weekly_remaining_after_request": (
            weekly_limit - weekly_used - 1
        ),
        "monthly_used": monthly_used,
        "monthly_limit": monthly_limit,
        "monthly_remaining_before_request": monthly_remaining,
        "monthly_remaining_after_request": (
            monthly_limit - monthly_used - 1
        ),
        "policy_source": policy["policy_documents"],
    }