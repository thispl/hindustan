import frappe
from frappe import _
from frappe.utils import today, getdate


def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_columns():
	return [
		{"label": _("Student"), "fieldname": "student", "fieldtype": "Data", "width": 200},
        {"label": _("Student Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 180},
        {"label": _("Fees"), "fieldname": "fees", "fieldtype": "Link", "options": "Fees", "width": 200},
        {"label": _("Institute"), "fieldname": "institute", "fieldtype": "Link", "options": "Institute", "width": 250},
        {"label": _("Academic Year"), "fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "width": 150},
        {"label": _("Academic Term"), "fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "width": 200},
        {"label": _("Program"), "fieldname": "program", "fieldtype": "Link", "options": "Program", "width": 300},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 150},
        {"label": _("Fee Category"), "fieldname": "fee_category", "fieldtype": "Data", "width": 400, "align": "left"},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150, "align": "right"},
        {"label": _("Amount Paid"), "fieldname": "amount_paid", "fieldtype": "Currency", "width": 150, "align": "right"},
        {"label": _("Outstanding Amount"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 190, "align": "right"},
	]

def get_data(filters):
	data = []
	conditions = {"docstatus": 1}
	if filters:
		if filters.get("student"):
			conditions["student"] = filters["student"]
		if filters.get("student_name"):
			conditions["student_name"] = filters["student_name"]
		if filters.get("custom_institute"):
			conditions["custom_institute"] = filters["custom_institute"]
		if filters.get("academic_year"):
			conditions["academic_year"] = filters["academic_year"]
		if filters.get("academic_term"):
			conditions["academic_term"] = filters["academic_term"]
		if filters.get("program"):
			conditions["program"] = filters["program"]
	fees = frappe.get_all("Fees",
		fields=["name", "student", "student_name", "custom_institute", "academic_year", "academic_term", "program", "due_date", "grand_total", "outstanding_amount"],
		filters=conditions,
	)
	total_amount = 0
	total_amount_paid = 0
	total_outstanding_amount = 0
	for f in fees:
		if (float(f.outstanding_amount)==0):
			status = "Paid"
		if (float(f.outstanding_amount) > 0 and f.due_date >= getdate(today())):
			status = "Unpaid"
		if (float(f.outstanding_amount) > 0 and f.due_date < getdate(today())):
			status = "Overdue"
		data.append({
			"fees": f"{f.name}",
            "student": f"<b>{f.student}</b>",
            "student_name": f"<b>{f.student_name}</b>",
            "institute": f"{f.custom_institute}",
            "academic_year": f"{f.academic_year}",
            "academic_term": f"{f.academic_term}",
            "program": f"{f.program}",
            "due_date": f"{f.due_date}",
            "status": f"<b>{status}</b>",
            "fee_category": "",
            "amount": f.grand_total,
            "amount_paid": f.grand_total - f.outstanding_amount,
            "outstanding_amount": f.outstanding_amount,
            "indent": 0,
		})
		fee_doc = frappe.get_doc("Fees", f.name)
		for comp in fee_doc.components:
			row = {
					"fees": "",
                	"student": "",
					"student_name": "",
					"institute": "",
					"academic_year": "",
					"academic_term": "",
					"program": "",
					"due_date": "",
					"status": "",
					"fee_category": f"{comp.fees_category}",
					"amount": f"{comp.amount}",
					"amount_paid": f"{comp.custom_amount_paid}",
					"outstanding_amount": f"{comp.custom_outstanding_amount}",
					"indent": 1
                }
			data.append(row)
		total_amount += f.grand_total
		total_amount_paid += f.grand_total - f.outstanding_amount
		total_outstanding_amount += f.outstanding_amount
	data.append(
		{
			"fees": "",
			"student": "",
			"student_name": "",
			"institute": "",
			"academic_year": "",
			"academic_term": "",
			"program": "",
			"due_date": "",
			"status": "",
			"fee_category": "<b>Total</b>",
			"amount": total_amount,
			"amount_paid": total_amount_paid,
			"outstanding_amount": total_outstanding_amount,
			"indent": 0
		}
	)
	return data

