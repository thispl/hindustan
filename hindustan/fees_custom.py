import requests
import xml.etree.ElementTree as ET
from cgi import print_environ
import requests,json
from datetime import date
from datetime import time,datetime
# import xmltodict
from os import name
from collections import namedtuple
import frappe
from numpy import empty
import pandas as pd
import json
import datetime
import calendar
from frappe.utils.csvutils import read_csv_content
from six.moves import range
from six import string_types
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,format_date,get_link_to_form,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime,date
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
import requests
from datetime import date, timedelta,time
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_url_to_form,money_in_words
import math
from frappe.utils.data import ceil, get_time, get_year_start
from datetime import datetime,date
from datetime import time



@frappe.whitelist()
def update_due_date(due,name):
    frappe.db.set_value("Fees",name,'due_date',due)
    # fee.reload()
    return "OK"


@frappe.whitelist()
def validate_advance_payments(doc, methods):
    registration_number= frappe.db.get_value("Student", doc.student, "custom_registration_number")
    if frappe.db.exists("Registration", registration_number):
        registration = frappe.get_doc("Registration", registration_number)
        if registration.amount_paid > 0:
            for row in doc.components:
                row.custom_amount_paid = 0
                if row.fees_category == "Registration Fee":
                    if registration.concession_applicability == 1:    
                        if registration.amount_paid <= registration.paid__payable_amount:
                            row.amount -= registration.concession_amount
                            row.custom_amount_paid = registration.amount_paid
                    else:
                        if registration.amount_paid <= registration.paid__payable_amount:
                            row.custom_amount_paid = registration.amount_paid                                                                                


# To get the total outstanding and total grand total
@frappe.whitelist()
def validate_outstanding_amount(doc, method):
    grand_total = 0
    outstanding = 0
    for row in doc.components: 
        out=row.amount - row.custom_amount_paid
        row.custom_outstanding_amount= out
        grand_total += row.amount
        outstanding +=out
    doc.grand_total = grand_total
    doc.outstanding_amount = outstanding
    doc.grand_total_in_words = money_in_words(grand_total)


def program_change_check(doc, method):

    if not doc.student or not doc.academic_term:
        return

    student = frappe.get_doc("Student", doc.student)

    if not student.custom_is_program_changed:
        return

    academic_semester = frappe.db.get_value("Academic Term",doc.academic_term,"custom_semester") or 0

    changed_sem = student.custom_sem__batch_ or 0

    condition_1 = (
        student.custom_previous_program
        and student.custom_previous_program == doc.program
        and changed_sem >= academic_semester
    )

    condition_2 = (
        student.custom_program
        and student.custom_program == doc.program
        and changed_sem < academic_semester
    )

    if condition_1 or condition_2:

        for row in doc.components:
            row.amount = 0
            # row.custom_amount_paid = 0
            # row.custom_outstanding_amount = 0

        doc.custom_remarks = "Program Changed"





