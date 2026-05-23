from frappe.model.document import Document
import frappe

class VisitingFaculty(Document):
    def validate(self):
        self.check_duplicate()

    def check_duplicate(self):
        if self.employee and self.from_date:
            duplicate = frappe.db.exists(
                "Visiting Faculty",
                {
                    "employee": self.employee,
                    "from_date": self.from_date,
                    "name": ["!=", self.name]    
                }
            )

            if duplicate:
                frappe.throw(
                    f"Entry already exists for Employee <b>{self.employee}</b> on date <b>{self.from_date}</b>. "
                )
