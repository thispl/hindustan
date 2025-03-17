import frappe
import json

from dateutil.relativedelta import relativedelta

import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond
from frappe.model.document import Document
from frappe.query_builder.functions import Coalesce, Count
from frappe.utils import (
    DATE_FORMAT,
    add_days,
    add_to_date,
    cint,
    comma_and,
    date_diff,
    flt,
    get_link_to_form,
    getdate,
)

from frappe.utils import cint, cstr, flt, money_in_words
from frappe.utils.background_jobs import enqueue
from frappe.model.mapper import get_mapped_doc
from education.education.doctype.fee_schedule.fee_schedule import FeeSchedule
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, formatdate, get_first_day,today


class CustomFeeSchedule(FeeSchedule):
    @frappe.whitelist()
    def create_fees(self):
        frappe.log_error(title="error in fee")
        self.db_set("fee_creation_status", "In Process")
        frappe.publish_realtime(
            "fee_schedule_progress", {"progress": "0", "reload": 1}, user=frappe.session.user
        )

        total_records = sum([int(d.total_students) for d in self.student_groups])
        if total_records > 10:
            frappe.msgprint(
                _(
                    """Fee records will be created in the background.
                In case of any error the error message will be updated in the Schedule."""
                )
            )
            enqueue(
                generate_fee,
                queue="default",
                timeout=6000,
                event="generate_fee",
                fee_schedule=self.name,
            )
        else:
            generate_fee(self.name)
def generate_fee(fee_schedule):
    doc = frappe.get_doc("Fee Schedule", fee_schedule)
    error = False
    total_records = sum([int(d.total_students) for d in doc.student_groups])
    created_records = 0

    if not total_records:
        frappe.throw(_("Please setup Students under Student Groups"))

    for d in doc.student_groups:
        students = get_students(
            d.student_group, doc.academic_year, doc.academic_term, doc.student_category
        )
        for student in students:
            try:
                fees_doc = get_mapped_doc(
                    "Fee Schedule",
                    fee_schedule,
                    {"Fee Schedule": {"doctype": "Fees", "field_map": {"name": "Fee Schedule"}}},
                )
                fees_doc.posting_date = doc.posting_date
                fees_doc.student = student.student
                fees_doc.student_name = student.student_name
                fees_doc.program = student.program
                fees_doc.program_enrollment = student.enrollment
                fees_doc.student_batch = student.student_batch_name
                fees_doc.send_payment_request = doc.send_email
                fees_doc.save()
                fees_doc.submit()
                created_records += 1
                frappe.publish_realtime(
                    "fee_schedule_progress",
                    {"progress": str(int(created_records * 100 / total_records))},
                    user=frappe.session.user,
                )

            except Exception as e:
                error = True
                err_msg = (
                    frappe.local.message_log and "\n\n".join(frappe.local.message_log) or cstr(e)
                )

    if error:
        frappe.db.rollback()
        frappe.db.set_value("Fee Schedule", fee_schedule, "fee_creation_status", "Failed")
        frappe.db.set_value("Fee Schedule", fee_schedule, "error_log", err_msg)

    else:
        frappe.db.set_value("Fee Schedule", fee_schedule, "fee_creation_status", "Successful")
        frappe.db.set_value("Fee Schedule", fee_schedule, "error_log", None)

    frappe.publish_realtime(
        "fee_schedule_progress", {"progress": "100", "reload": 1}, user=frappe.session.user
    )
    
# def get_students(student_group, academic_year, academic_term=None, student_category=None):
#     conditions = ""
#     args = [academic_year, student_group, academic_year]

#     if student_category:
#         conditions += " and pe.student_category=%s"
#         args.append(student_category)
#     if academic_term:
#         conditions += " and pe.academic_term=%s"
#         args.append(academic_term)

#     exclusion_condition = """
#         and pe.student not in (
#             select fee.student
#             from `tabFee` fee
#             where
#                 fee.docstatus = 1
#                 and fee.academic_year = %s
#                 {academic_term_condition}
#                 {student_category_condition}
#                 and fee.program = pe.program
#         )
#     """.format(
#         academic_term_condition="and fee.academic_term=%s" if academic_term else "",
#         student_category_condition="and fee.student_category=%s" if student_category else "",
#     )

#     if academic_term:
#         args.append(academic_term)
#     if student_category:
#         args.append(student_category)

#     try:
#         query = """
#             select pe.student, pe.student_name, pe.program, pe.student_batch_name, pe.name as enrollment
#             from `tabStudent Group Student` sgs, `tabProgram Enrollment` pe
#             where
#                 pe.docstatus = 1
#                 and pe.student = sgs.student
#                 and pe.academic_year = %s
#                 and sgs.parent = %s
#                 and sgs.active = 1
#                 {conditions}{exclusion_condition}
#         """.format(conditions=conditions, exclusion_condition=exclusion_condition)
        
#         frappe.log_error(query, "Debug: get_students Query")
#         frappe.log_error(args, "Debug: get_students Args")
        
#         students = frappe.db.sql(query, tuple(args), as_dict=1)
#         frappe.log_error(students, "Debug: get_students Output")
#         return students
#     except Exception as e:
#         frappe.log_error(message=str(e), title="Error in get_students")
#         return []

    
def get_students(student_group, academic_year, academic_term=None, student_category=None):
    # Build dynamic conditions and arguments
    conditions = []
    args = [academic_year, student_group]

    if student_category:
        conditions.append("pe.student_category = %s")
        args.append(student_category)

    if academic_term:
        conditions.append("pe.academic_term = %s")
        args.append(academic_term)

    # Join conditions with 'AND' or leave empty if no conditions
    conditions_clause = " AND " + " AND ".join(conditions) if conditions else ""

    # Construct the query
    query = f"""
        SELECT 
            pe.student, pe.student_name, pe.program, pe.student_batch_name, 
            pe.name AS enrollment, pe.student_category
        FROM 
            `tabStudent Group Student` sgs, `tabProgram Enrollment` pe
        WHERE
            pe.docstatus = 1 
            AND pe.student = sgs.student 
            AND pe.academic_year = %s
            AND sgs.parent = %s 
            AND sgs.active = 1
            {conditions_clause}
    """

    # Debug logs for validation
    frappe.log_error(message=query, title="Debug: Final SQL Query")
    frappe.log_error(message=str(args), title="Debug: SQL Query Arguments")

    # Execute query
    students = frappe.db.sql(query, args, as_dict=1)

    # Filter students that already have fee records
    filtered_students = [
        student
        for student in students
        if not frappe.db.exists(
            "Fees",
            {
                "student": student["student"],
                "program": student["program"],
                "academic_year": academic_year,
                "academic_term": academic_term,
                "student_category": student["student_category"],
                "student_batch": student["student_batch_name"],
                "docstatus":("!=",2)
            },
        )
    ]

    return filtered_students
