# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    columns += [
        _("Student Name") + ":Data/:100",
        _("Date Of Birth") + ":Date/:110",
        _("Program") + ":Link/Program:300",
        _("Institute Name") + ":Link/Institute:200",
        _("Payment Date") + ":Date/:120",
        _("Payment Mode") + ":Select/:200",
        _("Prospectus Fee") + ":Currency/:130",
        _("Paid Amount") + ":Currency/:120",
        _("Balance") + ":Float/:100",
        # _("Extra Amount") + ":Float/:120",
        _("Remarks") + ":Small Text/:300"
    ] 
    return columns

def get_data(filters):
    data = []
    conditions = ''
    params = {}
	
    if filters.from_date:
        conditions += " AND issue_date >= %(from_date)s"
        params["from_date"] = filters.from_date
        
    if filters.to_date:
        conditions += " AND issue_date <= %(to_date)s"
        params["to_date"] = filters.to_date

    if filters.institution_name:
        conditions += " AND institution_name = %(institution_name)s"
        params["institution_name"] = filters.institution_name 

    if filters.payment_mode:
        conditions += " AND payment_mode = %(payment_mode)s"
        params["payment_mode"] = filters.payment_mode

    prospectus_data = frappe.db.sql("""
        SELECT student_name, date_of_birth, program, institution_name, payment_date, payment_mode, prospectus_fee, paid_amount, remarks 
        FROM tabProspectus 
        WHERE docstatus = 1 {conditions} 
    """.format(conditions=conditions), params, as_dict=True)

    for i in prospectus_data:
        if i.docstatus != 2:
            balance = flt(i.prospectus_fee) - flt(i.paid_amount)
            extra = flt(i.paid_amount) - flt(i.prospectus_fee)
            # if balance<0:
            #     balance=0
            row = [i.student_name, i.date_of_birth, i.program, i.institution_name, i.payment_date,
                   i.payment_mode, i.prospectus_fee, i.paid_amount, balance, i.remarks]
            data.append(row)
    return data
