from app.tools.wfh import check_wfh_eligibility


result = check_wfh_eligibility.invoke({
    "employee_id": 1,
    "requested_date": "2026-10-08"
})

print(result)