import frappe
import requests
from dateutil.parser import parse as parse_datetime

def sync_attendance_from_external_api():
    api_config = frappe.get_doc("Hrms Api", "Hrms Api")
    api_url = api_config.link
    params = {"user_id": api_config.token}

    response = requests.get(api_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        return

    attendances = data.get("data", {}).get("attendances", [])

    for attendance in attendances:
        employee_data = attendance.get("employee", {})
        employee_id = employee_data.get("employee_id")
        in_time = attendance.get("in_time")
        out_time = attendance.get("out_time")

        if not employee_id or not in_time:
            continue

        try:
            in_time_parsed = parse_datetime(in_time)
        except Exception:
            continue

        if not frappe.db.exists("Employee Checkin", {
            "employee": employee_id,
            "time": in_time_parsed,
            "log_type": "IN"
        }):
            doc = frappe.new_doc("Employee Checkin")
            doc.update({
                "employee": employee_id,
                "log_type": "IN",
                "time": in_time_parsed
            })
            doc.insert(ignore_permissions=True)

        if out_time:
            try:
                out_time_parsed = parse_datetime(out_time)
            except Exception:
                continue

            if not frappe.db.exists("Employee Checkin", {
                "employee": employee_id,
                "time": out_time_parsed,
                "log_type": "OUT"
            }):
                doc = frappe.new_doc("Employee Checkin")
                doc.update({
                    "employee": employee_id,
                    "log_type": "OUT",
                    "time": out_time_parsed
                })
                doc.insert(ignore_permissions=True)
