# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from frappe.utils.data import add_days, add_years, today,getdate

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_columns():
    return [
        _("Institution") + ":Link/Institute:150",
        _("Student Name") + ":Link/Student:150",
        _("Program") + ":Link/Program:150",
        _("Student Category") + ":Link/Student Category:80",
        _("Start Date") + ":Start Date:120",
        _("End Date") + ":End Date:120",
        _("Registration Number") + ":Data:120",
        _("Payment Date") + ":Date:120",
        _("Registration Fee") + ":Float:120",
        _("Payable Amount") + ":Float:120",
        _("Concession Amount") + ":Float:120",
        _("Paid Amount") + ":Float:120",
        _("Outstanding Amount") + ":Float:120",
        _("Excess Amount") + ":Float:120",
        _("Payment Mode") + ":Select:150"
    ]

def get_data(filters):
    condition = add_filters(filters)
    sql, params = get_registration_data(condition)
    
    # Get the registration data based on the query and conditions
    registration_data = frappe.db.sql(sql, params, as_dict=True)
    
    # Process the data to match the columns
    data = []
    # frappe.errprint(registration_data)
    
    for row in registration_data:
        start_date = row.get("start_date")
        end_date = row.get("end_date")
        
        if start_date:
            start_date_str = start_date.strftime('%Y-%m-%d')
            start_date_str = datetime.strptime(start_date_str, "%Y-%m-%d") 
            formatted_start_date = start_date_str.strftime("%d-%m-%Y")
        else:
            formatted_start_date = " "  
        
        if end_date:
            end_date_str = end_date.strftime('%Y-%m-%d')
            end_date_str = datetime.strptime(end_date_str, "%Y-%m-%d") 
            formatted_end_date = end_date_str.strftime("%d-%m-%Y")
        else:
            formatted_end_date = ""  

        data.append({
            "institution": row.get("institution_name"),
            "student_name": row.get("student_name"),
            "program": row.get("program"),
            "student_category": row.get("student_category"),
            "start_date": formatted_start_date,
            "end_date": formatted_end_date,
            "registration_number": row.get("registration_number"),
            "payment_date": row.get("payment_date"),
            "registration_fee": row.get("course_registration_fee"),
            "payable_amount": row.get("paid__payable_amount"),
            "concession_amount": row.get("concession_amount"),
            "paid_amount": row.get("amount_paid"),
            "outstanding_amount": row.get("outstanding_amount"),
            "excess_amount": row.get('excess_amount'),
            "payment_mode": row.get("payment_mode")
        })
    
    return data


def add_filters(filters):
    condition = {
        "docstatus": ["!=", 2],
        "start_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
        "end_date": ["between", [filters.get("from_date"), filters.get("to_date")]]
    }
    # frappe.errprint(filters)
    if filters.get("from_date"):
        condition["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        condition["to_date"] = filters.get("to_date")
    
    if filters.get("institution"):
        condition["institution_name"] = filters.get("institution")
    
    if filters.get("program"):
        condition["program"] = filters.get("program")
    
    if filters.get("course"):
        condition["course_name"] = filters.get("course")
    
    if filters.get("student_category"):
        condition["student_category"] = filters.get("student_category")
    
    if filters.get("registration_number"):
        condition["name"] = filters.get("registration_number")
    
    if filters.get("academic_year"):
        condition["academic_year"] = filters.get("academic_year")
    
    if filters.get("concession_applicability"):
        condition["concession_applicability"] = filters.get("concession_applicability")
    
    if filters.get("payment_mode"):
        # frappe.errprint(filters.get("payment_mode"))
        condition["payment_mode"] = filters.get("payment_mode")
    
    if filters.get("due_payment"):
        condition["outstanding_amount"] = filters.get("due_payment")
    
    return condition

def get_registration_data(condition):
    sql = """
        SELECT 
        institution_name, student_name, program, course_name, student_category, payment_date,
        start_date, end_date, registration_number, course_registration_fee, 
        paid__payable_amount, concession_amount, amount_paid, outstanding_amount, excess_amount, payment_mode
    FROM `tabRegistration`
    WHERE docstatus = 1
    """
    
    params = []
    # frappe.errprint(condition)
    # Add dynamic conditions to the SQL query based on the filters
    if "institution_name" in condition:
        sql += " AND institution_name = %s"
        params.append(condition["institution_name"])


    if "name" in condition:
        sql += " AND name = %s"
        params.append(condition["name"])

    if "academic_year" in condition:
        sql += " AND academic_year = %s"
        params.append(condition["academic_year"])
    
    if "program" in condition:
        sql += " AND program = %s"
        params.append(condition["program"])
    if "student_category" in condition:
        sql += " AND student_category = %s"
        params.append(condition["student_category"])
    if "concession_applicability" in condition:
        sql += " AND concession_applicability = 1"  
    else:
        sql += " AND concession_applicability = 0" 

    if "payment_mode" in condition:
        # frappe.errprint(condition["payment_mode"])
        sql += " AND payment_mode = %s"
        params.append(condition["payment_mode"])

    if "outstanding_amount" in condition:
        sql += " AND outstanding_amount = %s"
        params.append(condition["outstanding_amount"])

    if "start_date" in condition and "end_date" in condition:
        sql += " AND payment_date BETWEEN %s AND %s"
        params.append(condition["from_date"])
        params.append(condition["to_date"])
    sql += " ORDER BY start_date ASC"


    # if "end_date" in condition and "start_date" not in condition:
    #     sql += " AND end_date BETWEEN %s AND %s"
    #     params.append(condition["end_date"])
    #     params.append(condition["end_date"])

    

    return sql, params
