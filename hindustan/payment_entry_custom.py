
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

# Creating student log while submitting the payment entry
@frappe.whitelist()
def create_student_log_on_payment(doc, method):
    if doc.party_type == "Student":
        sl = frappe.new_doc("Student Log")
        sl.student = doc.party
        for ref in doc.references:
            if ref.reference_doctype == "Fees":
                fee = frappe.get_doc("Fees", ref.reference_name)
                sl.type = "Payment"
                sl.date = today()
                sl.academic_year = fee.academic_year
                sl.academic_term = fee.academic_term
                sl.program = fee.program
                sl.student_batch = fee.student_batch
                fee_name = ref.reference_name
                message = f"Amount &#8377; {doc.total_allocated_amount} paid against the Payment Entry - <b><a href='http://139.5.188.247/app/payment-entry/{doc.name}'>{doc.name} and Fees - <b><a href='http://139.5.188.247/app/fees/{fee_name}'>{fee_name}</b></b>"
                message += "<table>"
                message += """<tr>
                                <td><b>Fees Category</b></td>
                                <td><b>Description</b></td>
                                <td><b>Amount</b></td>
                                <td><b>Amount Paid</b></td>
                                <td><b>Balance</b></td>
                            </tr>"""
                tot_paid = 0
                for comp in fee.components:
                    balance = comp.amount - comp.custom_amount_paid
                    tot_paid += comp.custom_amount_paid
                    message += f"""<tr>
                                    <td>{comp.fees_category}</td>
                                    <td>{comp.description}</td>
                                    <td>{comp.amount}</td>
                                    <td>{comp.custom_amount_paid}</td>
                                    <td>{balance}</td>
                                </tr>"""
                message += f"""<tr>
                                    <td></td>
                                    <td><b>Total</b></td>
                                    <td><b>{fee.grand_total}</b></td>
                                    <td><b>{tot_paid}</b></td>
                                    <td><b>{fee.outstanding_amount}</b></td>
                                </tr>"""
                message += "</table>"
                sl.log = message
                sl.save()


# Delete student log when cancelling the payment entry
@frappe.whitelist()
def delete_student_log_on_payment(doc, method):
    student_log = frappe.db.sql("""SELECT name FROM `tabStudent Log` WHERE log LIKE '%s'"""%(f"%{doc.name}%"),as_dict=True)
    if student_log:
        sl = frappe.get_doc("Student Log", student_log[0].name)
        sl.delete()
