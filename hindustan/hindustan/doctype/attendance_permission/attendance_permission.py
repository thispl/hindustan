import frappe
from frappe.model.document import Document

class AttendancePermission(Document):
    def validate(self):
        existing = frappe.db.exists(
            "Attendance Permission",
            {
                "employee": self.employee,
                "permission_date": self.permission_date,
                "docstatus": ["!=", 2], 
                "name": ["!=", self.name]  
            }
        )

        if existing:
            frappe.throw(("Permission already exists for this employee on this date: {0}").format(existing))


    def on_submit(self):
        att = frappe.db.exists(
            "Attendance",
            {"employee": self.employee, "attendance_date": self.permission_date}
        )

        if att:
            att_doc = frappe.get_doc("Attendance", att)
            att_doc.custom_permission = self.name
            att_doc.custom_permission_hours = self.total_time
            att_doc.custom_original_shift = att_doc.shift
            att_doc.shift = self.shift
            att_doc.save(ignore_permissions=True)
        else:
            att_doc = frappe.new_doc("Attendance")
            att_doc.employee = self.employee
            att_doc.attendance_date = self.permission_date
            att_doc.status = "Absent"  
            att_doc.custom_permission = self.name
            att_doc.custom_permission_hours = self.total_time
            att_doc.custom_original_shift = att_doc.shift
            att_doc.shift = self.shift
            att_doc.insert(ignore_permissions=True)

    def on_cancel(self):
        att_name = frappe.db.exists(
            "Attendance",
            {"employee": self.employee, "attendance_date": self.permission_date}
        )

        if att_name:
            att_doc = frappe.get_doc("Attendance", att_name)
            att_doc.shift = att_doc.custom_original_shift
            att_doc.custom_permission = ""
            att_doc.custom_permission_hours = ""
            att_doc.save(ignore_permissions=True)

