from app.tools.wfh import get_wfh_usage

result = get_wfh_usage.invoke({
    "employee_id": 1
})

print(result)