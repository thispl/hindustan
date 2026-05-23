import frappe
from frappe import _
from frappe.utils import today, getdate
from datetime import datetime

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_columns():
    return [
        {"label": _("Student"), "fieldname": "student", "fieldtype": "Data", "width": 200},
        {"label": _("Student Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 180},
        {"label": _("Admission"), "fieldname": "admission", "fieldtype": "Link", "options": "Admission", "width": 200},
        {"label": _("Fees"), "fieldname": "fees", "fieldtype": "Link", "options": "Fees", "width": 200},
        {"label": _("Institute"), "fieldname": "institute", "fieldtype": "Link", "options": "Institute", "width": 250},
        {"label": _("Academic Year"), "fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "width": 150},
        {"label": _("Academic Term"), "fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "width": 200},
        {"label": _("Semester"), "fieldname": "semester", "fieldtype": "Data", "width": 200},
        {"label": _("Program"), "fieldname": "program", "fieldtype": "Link", "options": "Program", "width": 300},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 150},
        {"label": _("Fee Category"), "fieldname": "fee_category", "fieldtype": "Data", "width": 400, "align": "left"},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150, "align": "right"},
        {"label": _("Amount Paid"), "fieldname": "amount_paid", "fieldtype": "Currency", "width": 150, "align": "right"},
        {"label": _("Outstanding Amount"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 190, "align": "right"},
    ]

import frappe
from frappe.utils import getdate, today

def get_data(filters):
    data = []
    
    # Base conditions
    conditions = ["f.docstatus = 1"]
    values = {}

    # Applying additional filters
    if filters:
        if filters.get("student"):
            conditions.append("f.student = %(student)s")
            values["student"] = filters["student"]
        if filters.get("student_name"):
            conditions.append("f.student_name = %(student_name)s")
            values["student_name"] = filters["student_name"]
        if filters.get("custom_institute"):
            conditions.append("f.custom_institute = %(custom_institute)s")
            values["custom_institute"] = filters["custom_institute"]
        if filters.get("academic_year"):
            conditions.append("f.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]
        if filters.get("academic_term"):
            conditions.append("f.academic_term = %(academic_term)s")
            values["academic_term"] = filters["academic_term"]
        if filters.get("program"):
            conditions.append("f.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("admission"):
            conditions.append("s.custom_admission_number = %(admission)s")
            values["admission"] = filters["admission"]

    # Construct SQL query with dynamic filters
    fees = frappe.db.sql(f"""
        SELECT f.name, f.student, f.student_name, s.custom_admission_number AS admission, 
               f.custom_institute, f.academic_year, f.academic_term, f.program, 
               f.due_date, f.grand_total, f.outstanding_amount
        FROM `tabFees` f
        JOIN `tabStudent` s ON f.student = s.name
        WHERE {" AND ".join(conditions)}
        ORDER BY s.custom_admission_number
    """, values, as_dict=True)

    total_amount = total_amount_paid = total_outstanding_amount = 0

    for f in fees:
        outstanding_amount = float(f.outstanding_amount)
        status = "Paid" if outstanding_amount == 0 else "Unpaid" if f.due_date >= getdate(today()) else "Overdue"
        if f.due_date:
            due_date_str = f.due_date.strftime('%Y-%m-%d')
            due_date_str = datetime.strptime(due_date_str, "%Y-%m-%d") 
            formatted_due_date = due_date_str.strftime("%d-%m-%Y")
        else:
            formatted_due_date=''
        sem=frappe.db.get_value('Academic Term',{'name': f.academic_term},['custom_semester'])
        if not sem:
            sem=0
        data.append({
            "fees": f.name,
            "student": f"<b>{f.student}</b>",
            "student_name": f"<b>{f.student_name}</b>",
            "admission": f.admission,
            "institute": f.custom_institute,
            "academic_year": f.academic_year,
            "academic_term": f.academic_term,
            'semester':sem,
            "program": f.program,
            "due_date": formatted_due_date,
            "status": f"<b>{status}</b>",
            "fee_category": "",
            "amount": f.grand_total,
            "amount_paid": f.grand_total - outstanding_amount,
            "outstanding_amount": outstanding_amount,
            "indent": 0,
        })

        # Fetch fee components in a single query
        components = frappe.db.sql("""
            SELECT fees_category, amount, custom_amount_paid, custom_outstanding_amount 
            FROM `tabFee Component` 
            WHERE parent = %s
        """, (f.name,), as_dict=True)

        for comp in components:
            data.append({
                "fees": "",
                "student": "",
                "student_name": "",
                "institute": "",
                "academic_year": "",
                "academic_term": "",
                'semester':'',
                "program": "",
                "due_date": "",
                "status": "",
                "fee_category": comp.fees_category,
                "amount": comp.amount,
                "amount_paid": comp.custom_amount_paid,
                "outstanding_amount": comp.custom_outstanding_amount,
                "indent": 1
            })

        # Update totals
        total_amount += f.grand_total
        total_amount_paid += f.grand_total - outstanding_amount
        total_outstanding_amount += outstanding_amount

    # Append total row
    data.append({
        "fees": "",
        "student": "",
        "student_name": "",
        "institute": "",
        "academic_year": "",
        "academic_term": "",
        'semester':'',
        "program": "",
        "due_date": "",
        "status": "",
        "fee_category": "<b>Total</b>",
        "amount": total_amount,
        "amount_paid": total_amount_paid,
        "outstanding_amount": total_outstanding_amount,
        "indent": 0
    })

    return data
