import requests
import xml.etree.ElementTree as ET
from cgi import print_environ
import requests,json
from datetime import date
from datetime import time,datetime
import xmltodict
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
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,format_date,
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
#create or update the Overall Fee Structure on submitting the Fee Structure Document
def create_update_overall_fee_structure(doc,method):
    fee_structures=frappe.get_all("Fee Structure",{'program':doc.program,'student_category':doc.student_category,"academic_year":doc.academic_year,'docstatus':("!=",2)},['name'])
    fee_data = {}
    for fee_structure in fee_structures:
        fee_stru = frappe.get_doc("Fee Structure", fee_structure.name)
        for c in fee_stru.components:
            if c.fees_category not in fee_data:
                fee_data[c.fees_category] = {f"sem_{i}": 0 for i in range(1, 9)}  

            semester_key = f"sem_{fee_stru.custom_semester}" 
            if semester_key in fee_data[c.fees_category]:
                fee_data[c.fees_category][semester_key] += c.amount 
    grand_total = {f"sem_{i}": 0 for i in range(1, 9)}
    if frappe.db.exists("Overall Fee Structure",{'program':doc.program,'student_category':doc.student_category,"academic_year":doc.academic_year}):
        overall_fee_stru = frappe.get_doc("Overall Fee Structure",{'program':doc.program,'student_category':doc.student_category,"academic_year":doc.academic_year})
        overall_fee_stru.set('fee_structure', [])
        for category, sem_data in fee_data.items():
            for sem_key, amount in sem_data.items():
                grand_total[sem_key] += amount
            overall_fee_stru.append('fee_structure', {
                'fees_category': category,
                **sem_data  
            })
        overall_fee_stru.append('fee_structure', {
            'fees_category': 'Total',
            **grand_total,
        })
        overall_fee_stru.save(ignore_permissions=True)
    else:
        overall_fee_stru = frappe.new_doc("Overall Fee Structure")
        overall_fee_stru.program = doc.program
        overall_fee_stru.academic_year = doc.academic_year
        overall_fee_stru.student_category=doc.student_category
        for category, sem_data in fee_data.items():
            for sem_key, amount in sem_data.items():
                grand_total[sem_key] += amount
            overall_fee_stru.append('fee_structure', {
                'fees_category': category,
                **sem_data  
            })
        overall_fee_stru.append('fee_structure', {
            'fees_category': 'Total',
            **grand_total,
        })
        overall_fee_stru.save(ignore_permissions=True)
        frappe.db.commit()
        
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

# To get the total outstanding and total grand total
@frappe.whitelist()
def validate_outstanding_amount(doc, method):
    grand_total = 0
    outstanding = 0
    for row in doc.components: 
        row.custom_outstanding_amount= row.amount - row.custom_amount_paid
        grand_total += row.amount
        outstanding += row.custom_outstanding_amount
    doc.grand_total = grand_total
    doc.outstanding_amount = outstanding
    doc.grand_total_in_words = money_in_words(grand_total)

#leave application restrict condition
import frappe
from frappe.utils import today, date_diff
from datetime import datetime
@frappe.whitelist()
def leave_restriction_el(doc, method):
    if doc.leave_type == 'Casual Leave':
        from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
        to_date = datetime.strptime(doc.to_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')
        prev_day = frappe.utils.add_days(from_date, -1)
        next_day = frappe.utils.add_days(to_date, 1)
        prev_working_day = get_next_working_day(prev_day, holiday_list, direction='backward')
        next_working_day = get_next_working_day(next_day, holiday_list, direction='forward')
        employment_type = frappe.db.get_value('Employee', doc.employee, 'employment_type')
        if employment_type == 'Non - Teaching Staff':
           
            existing_earned_leave_before = frappe.db.exists('Leave Application', {
                'employee': doc.employee,
                'from_date': prev_working_day.strftime('%Y-%m-%d'),
                'leave_type': 'Earned Leave',
                'docstatus': ('!=', 2)  
            })
            
            # Check if there is any earned leave on the next working day
            existing_earned_leave_after = frappe.db.exists('Leave Application', {
                'employee': doc.employee,
                'from_date': next_working_day.strftime('%Y-%m-%d'),
                'leave_type': 'Earned Leave',
                'docstatus': ('!=', 2)  # Status is not 'Cancelled'
            })
            
           
            if existing_earned_leave_before:
                frappe.throw(
                    "Since you have already applied Earned Leave, you should only apply Earned Leave and not allow Casual Leave."
                )
            if existing_earned_leave_after:
                frappe.throw(
                    "Since you have already applied Earned Leave, you should only apply Earned Leave and not allow Casual Leave."
                )

def get_next_working_day(date, holiday_list, direction='forward'):
    while True:
        day_of_week = date.weekday()
        week_number = (date.day - 1) // 7 + 1
        is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': date.strftime('%Y-%m-%d')})
        # Second and fourth Saturdays are holidays
        if not is_holiday and not (day_of_week == 5 and (week_number == 2 or week_number == 4)):
            break
        date = frappe.utils.add_days(date, 1 if direction == 'forward' else -1)
    return date


#Leave Restrict Casual
import frappe
from frappe.utils import today, date_diff
from datetime import datetime
@frappe.whitelist()
def leave_restriction_cl(doc, method):
   
    if doc.leave_type == 'Earned Leave':
       
        from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
        to_date = datetime.strptime(doc.to_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
        
        
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')

       
        prev_day = frappe.utils.add_days(from_date, -1)
        
        
        next_day = frappe.utils.add_days(to_date, 1)

        
        prev_working_day = get_next_working_day(prev_day, holiday_list, direction='backward')
        next_working_day = get_next_working_day(next_day, holiday_list, direction='forward')

        
        employment_type = frappe.db.get_value('Employee', doc.employee, 'employment_type')
        if employment_type == 'Non - Teaching Staff':
            # Check if there is any earned leave on the previous working day
            existing_earned_leave_before = frappe.db.exists('Leave Application', {
                'employee': doc.employee,
                'from_date': prev_working_day.strftime('%Y-%m-%d'),
                'leave_type': 'Casual Leave',
                'docstatus': ('!=', 2)  # Status is not 'Cancelled'
            })
            
            # Check if there is any earned leave on the next working day
            existing_earned_leave_after = frappe.db.exists('Leave Application', {
                'employee': doc.employee,
                'from_date': next_working_day.strftime('%Y-%m-%d'),
                'leave_type': 'Casual Leave',
                'docstatus': ('!=', 2)  # Status is not 'Cancelled'
            })
            
            
            if existing_earned_leave_before:
                frappe.throw(
                    "Since you have already applied Casual Leave, you should only apply Casual Leave and not allow Earned Leave."
                )
            if existing_earned_leave_after:
                frappe.throw(
                    "Since you have already applied Casual Leave, you should only apply Casual Leave and not allow Earned Leave."
                )

def get_next_working_day(date, holiday_list, direction='forward'):
    while True:
        day_of_week = date.weekday()
        week_number = (date.day - 1) // 7 + 1
        is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': date.strftime('%Y-%m-%d')})
        # Second and fourth Saturdays are holidays
        if not is_holiday and not (day_of_week == 5 and (week_number == 2 or week_number == 4)):
            break
        date = frappe.utils.add_days(date, 1 if direction == 'forward' else -1)
    return date



#Leave Application Restrict for Teaching Employee
import frappe
from frappe.utils import today, add_days
from datetime import datetime

from frappe.utils import today, add_days
from datetime import datetime

@frappe.whitelist()
def leave_restriction_cl_teaching(doc, method):
   
    if not doc.get("__islocal"):
        return

  
    from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
    to_date = datetime.strptime(doc.to_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date

    
    holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')
    if not holiday_list:
        frappe.throw(f"Holiday List is not defined for employee {doc.employee}")

  
    prev_day = add_days(from_date, -1)

   
    is_prev_day_vacation = frappe.db.exists('Holiday', {
        'parent': holiday_list,
        'holiday_date': prev_day.strftime('%Y-%m-%d'),
        'is_vacation': 1
    })

    if is_prev_day_vacation and doc.leave_type == "Casual Leave":
        frappe.throw(
            "You are not allowed to apply for Casual Leave on this day because the previous day has been marked as a vacation."
        )
    employment_type = frappe.db.get_value('Employee', doc.employee, 'employment_type')
    if employment_type == 'Teaching Staff':
        next_day = add_days(to_date, 1) if to_date else None

        next_working_day = get_next_working_day(next_day, holiday_list, direction='forward') if next_day else None
        if next_working_day:
            existing_cl_after = frappe.db.exists('Leave Application', {
                'employee': doc.employee,
                'from_date': next_working_day.strftime('%Y-%m-%d'),
                'leave_type': 'Casual Leave',
                'docstatus': ['!=', 2]
            })

            if existing_cl_after:
                frappe.throw(
                    "You are not allowed to apply for Casual Leave on this day because the after day has been marked as a vacation."
                )


def get_next_working_day(date, holiday_list, direction='forward'):
    while True:
        # Check if the date is a holiday
        is_holiday = frappe.db.exists('Holiday', {
            'parent': holiday_list,
            'holiday_date': date.strftime('%Y-%m-%d'),
            'is_vacation': 1
        })

        # If it's not a holiday, return the date
        if not is_holiday:
            break

        # Move to the next or previous day depending on the direction
        date = add_days(date, 1 if direction == 'forward' else -1)

    return date


#Leave Allocation Non Teaching Staff
@frappe.whitelist()
def allocate_leaves_automatically():
   
    employees = frappe.get_all(
        'Employee',
        filters={'status': 'Active', 'employment_type': 'Non - Teaching Staff'},
        fields=['name', 'employee', 'date_of_joining']
    )
    today = datetime.today().date()
    current_year = today.year
    casual_leave = 12  
    earned_leave_per_month = 25
    current_date = datetime.now().date()
    for employee in employees:
        doj = employee.date_of_joining
        diff = current_date - doj
        years = diff.days / 365.25 
        print(years)
        if(int(years)) > 0 :
            earned_leave_allocation = earned_leave_per_month
            existing_allocation = frappe.db.exists('Leave Allocation', {
                'employee': employee.name,
                'leave_type': 'Earned Leave',
                'from_date': f'{current_year}-01-01',
                'to_date': f'{current_year}-12-31',
                'docstatus': 1
            })
            if not existing_allocation:
                closing_balance = get_closing_balance(employee.name, 'Earned Leave', f'{current_year}-01-01')
                if closing_balance > 50:
                    total_allocation = 50
                else:
                    total_allocation = closing_balance + earned_leave_allocation
                create_leave_allocation(employee.name, 'Earned Leave', current_year, total_allocation)
            existing_casual_allocation = frappe.db.exists('Leave Allocation', {
                'employee': employee.name,
                'leave_type': 'Casual Leave',
                'from_date': f'{current_year}-01-01',
                'to_date': f'{current_year}-12-31',
                'docstatus': 1
            })
            if not existing_casual_allocation:
                create_leave_allocation(employee.name, 'Casual Leave', current_year, casual_leave)
        else:
            frappe.log_error(
                title="Employee not eligible for leave allocation",
                message=f"Employee {employee.name} has not completed a year of service yet."
            )

def get_closing_balance(employee, leave_type, from_date):
    opening_balance = get_opening_balance(employee, leave_type, from_date)
    availed_leaves = get_availed_leaves(employee, leave_type, from_date)
    closing_balance = opening_balance - availed_leaves
    return closing_balance if closing_balance >= 0 else 0

def create_leave_allocation(employee, leave_type, year, total_allocation):
    leave_allocation = frappe.new_doc('Leave Allocation')
    leave_allocation.employee = employee
    leave_allocation.leave_type = leave_type
    leave_allocation.new_leaves_allocated = total_allocation
    leave_allocation.from_date = f"{year}-01-01"
    leave_allocation.to_date = f"{year}-12-31"
    leave_allocation.docstatus = 1
    leave_allocation.flags.ignore_permissions = True
    leave_allocation.insert()
    leave_allocation.submit()
    frappe.log_error(
        title="Leave Allocation Created",
        message=f"Leave allocation created for {employee} ({leave_type}) for the year {year}."
    )

def get_opening_balance(employee, leave_type, from_date):
    opening = frappe.db.sql("""
        SELECT SUM(la.leaves) as total
        FROM `tabLeave Ledger Entry` AS la
        WHERE la.employee = %s 
        AND la.leave_type = %s
        AND la.from_date < %s
        AND la.transaction_type = 'Leave Application'
    """, (employee, leave_type, from_date))
    total_leaves_allocated = frappe.db.sql("""
        SELECT SUM(total_leaves_allocated) 
        FROM `tabLeave Allocation` 
        WHERE employee = %s
        AND leave_type = %s
        AND from_date < %s
    """, (employee, leave_type, from_date))
    opening_balance = (opening[0][0] if opening and opening[0][0] is not None else 0) + \
                      (total_leaves_allocated[0][0] if total_leaves_allocated and total_leaves_allocated[0][0] is not None else 0)
    return opening_balance

def get_availed_leaves(employee, leave_type, from_date):
    availed = frappe.db.sql("""
        SELECT SUM(total_leave_days) 
        FROM `tabLeave Application` 
        WHERE employee = %s 
        AND leave_type = %s 
        AND status = 'Approved'
        AND from_date >= %s 
    """, (employee, leave_type, from_date))

    return availed[0][0] if availed and availed[0][0] is not None else 0

#Teaching Employees Casual Leave Creation
@frappe.whitelist()
def allocate_leaves_automatically_teaching():
    # Fetch employees who are Non-Teaching Staff and Active
    employees = frappe.get_all(
        'Employee',
        filters={'status': 'Active', 'employment_type': 'Teaching Staff'},
        fields=['name', 'employee', 'date_of_joining']
    )

    today = datetime.today().date()
    current_year = today.year
    casual_leave = 12	
    for employee in employees:
        print(current_year)
        date_of_joining = employee.date_of_joining
        if (today - date_of_joining).days > 365:
            
            existing_allocation = frappe.db.exists('Leave Allocation', {
                'employee': employee.name,
                'from_date': ['>=', f'{current_year}-01-01'],
                'to_date': ['<=', f'{current_year}-12-31'],
                'docstatus': ['!=', 2]
            })	
            print(existing_allocation)
            if not existing_allocation:
                
                create_leave_allocation(employee.name, 'Casual Leave', current_year, casual_leave)
        else:
            
            frappe.log_error(title="Employee not eligible for leave allocation", message=f"Employee {employee.name} has not completed a year of service yet.")


def create_leave_allocation(employee, leave_type, year, new_leaves):
    previous_balance = get_previous_balance(employee, leave_type)
    total_allocation = previous_balance + new_leaves	
    leave_allocation = frappe.new_doc('Leave Allocation')
    leave_allocation.employee = employee
    leave_allocation.leave_type = leave_type
    leave_allocation.new_leaves_allocated = total_allocation
    leave_allocation.year = year
    leave_allocation.from_date = f"{year}-01-01"
    leave_allocation.to_date = f"{year}-12-31"
    leave_allocation.flags.ignore_permissions = True
    leave_allocation.insert()
    leave_allocation.submit()
    frappe.log_error(title="Leave Allocation Created", message=f"Leave allocation created for {employee} ({leave_type}) for the year {year}.")


def get_previous_balance(employee, leave_type):
    closing_balance = frappe.db.sql("""
        SELECT SUM(leaves) 
        FROM `tabLeave Ledger Entry`
        WHERE employee = %s AND leave_type = %s AND is_expired = 0
    """, (employee, leave_type))
    return closing_balance[0][0] if closing_balance and closing_balance[0][0] else 0

#Instructor Creation
import frappe
@frappe.whitelist()
def teaching_type(doc, method):
   
    if doc.employment_type == 'Teaching Staff' and doc.status == 'Active':
       
        existing_instructor = frappe.db.exists("Instructor", {"employee": doc.name})
        
        if not existing_instructor:
           
            instructor_doc = frappe.new_doc("Instructor")
            instructor_doc.instructor_name = doc.employee_name
            instructor_doc.employee = doc.name
            instructor_doc.department = doc.department
            instructor_doc.gender = doc.gender
            instructor_doc.status = doc.status
            instructor_doc.custom_institute_name = doc.custom_institute_name

            instructor_doc.insert(ignore_permissions=True)

            
            frappe.log_error(
                title="Instructor Created",
                message=f"Instructor document created for employee {doc.name}"
            )


@frappe.whitelist()
def update_due_date(due,name):
    frappe.db.set_value("Fees",name,'due_date',due)
    # fee.reload()
    return "OK"



def leave_restriction_el_before(doc, method):
    # when el is applied after an holiday and another leave application is present before the holiday, then it is restricted
    if doc.leave_type=='Earned Leave':
        from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
        previous_date = frappe.utils.add_days(from_date, -1)    
        while True:
            is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list,'holiday_date': previous_date.strftime('%Y-%m-%d')})
            if not is_holiday:
                break      
            previous_date = frappe.utils.add_days(previous_date, -1)   
        # check any application present on previous day    
        existing_leave_from = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name': ('!=', doc.name),
            'from_date': previous_date.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        
        existing_leave_to = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name': ('!=', doc.name),
            'to_date': previous_date.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        
        if existing_leave_from or existing_leave_to:
            frappe.throw('Another leave application with leave leave type Earned Leave is found before the holiday.Kindly combine and put as single application')

@frappe.whitelist()
def leave_restriction_el_after(doc, method):
    # when el is applied before an holiday and another leave application is present after the holiday, then it is restricted
    if doc.leave_type=='Earned Leave':
        to_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
        next_day = frappe.utils.add_days(to_date, 1)
        while True:
            is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': next_day.strftime('%Y-%m-%d')})
            if not is_holiday:
                break
            next_day = frappe.utils.add_days(next_day, 1)
        # check any application present on next day    
        existing_leave_from = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name':('!=', doc.name),
            'from_date': next_day.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        existing_leave_to = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name':('!=', doc.name),
            'to_date': next_day.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })   
        if existing_leave_from or existing_leave_to:
            frappe.throw('Another leave application with leave leave type Earned Leave is found after the holiday.Kindly combine and put as single application')

@frappe.whitelist()
def leave_restriction_combining_after(doc, method):
    # when el is applied before an holiday and another leave application is present after the holiday, then it is restricted
    if doc.leave_type=='Earned Leave' or doc.leave_type=='Casual Leave':
        to_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
        next_day = frappe.utils.add_days(to_date, 1)
        while True:
            is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': next_day.strftime('%Y-%m-%d')})
            if not is_holiday:
                break
            next_day = frappe.utils.add_days(next_day, 1)
        # check any application present on next day   
        if doc.leave_type=='Earned Leave':
            lt='Casual Leave'
        else:
            lt='Earned Leave'
        existing_leave_from = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name':('!=', doc.name),
            'from_date': next_day.strftime('%Y-%m-%d'),
            'leave_type': lt,
            'docstatus': ('!=', 2)
        })
        existing_leave_to = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name':('!=', doc.name),
            'to_date': next_day.strftime('%Y-%m-%d'),
            'leave_type': lt,
            'docstatus': ('!=', 2)
        })   
        if existing_leave_from or existing_leave_to:
            frappe.throw(f"Not allowed to combine {lt} and {doc.leave_type}")

def leave_restriction_combining_before(doc, method):
    # when el is applied after an holiday and another leave application is present before the holiday, then it is restricted
    if doc.leave_type=='Earned Leave' or doc.leave_type=='Casual Leave':
        from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
        previous_date = frappe.utils.add_days(from_date, -1)    
        while True:
            is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list,'holiday_date': previous_date.strftime('%Y-%m-%d')})
            if not is_holiday:
                break      
            previous_date = frappe.utils.add_days(previous_date, -1)   
        if doc.leave_type=='Earned Leave':
            lt='Casual Leave'
        else:
            lt='Earned Leave'
        existing_leave_from = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name': ('!=', doc.name),
            'from_date': previous_date.strftime('%Y-%m-%d'),
            'leave_type': lt,
            'docstatus': ('!=', 2)
        })
        
        existing_leave_to = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name': ('!=', doc.name),
            'to_date': previous_date.strftime('%Y-%m-%d'),
            'leave_type': lt,
            'docstatus': ('!=', 2)
        })
        if existing_leave_from or existing_leave_to:
            frappe.throw(f"Not allowed to combine {lt} and {doc.leave_type}")

@frappe.whitelist()
def create_el_allocation():
    current_date=datetime.today()
    # current_date=add_days(current_date,-10)
    current_month_day = current_date.strftime('%m-%d')
    last_date_of_year = date(current_date.year, 12, 31)
    first_date_of_year = date(current_date.year, 1, 1)
    if current_date!=last_date_of_year:
        print("pass")
        print(current_month_day)
        previous_year=current_date.year-1 
        emp=frappe.db.sql("""SELECT name, employee_name, date_of_joining FROM `tabEmployee` WHERE YEAR(date_of_joining) = %(year)s AND status = 'Active' AND DATE_FORMAT(date_of_joining, '%%m-%%d') = %(month_day)s""", {'year': previous_year, 'month_day': current_month_day})    
        for e in emp:
            print(e[1])
            mcount=0
            join_date=e[2]
            temp_date=join_date
            days_in_month = calendar.monthrange(temp_date.year, temp_date.month)[1]
            temp_date+=timedelta(days=days_in_month)
            while temp_date.year==previous_year:
                mcount+=1
                days_in_month = calendar.monthrange(temp_date.year, temp_date.month)[1]
                temp_date+=timedelta(days=days_in_month)
            if temp_date.year!=previous_year:
                days_in_month = calendar.monthrange(temp_date.year, temp_date.month)[1]
                temp_date-=timedelta(days=days_in_month)
                if temp_date.month == 12: 
                    if join_date.day < 10:
                        mcount += 1
                    elif 10 <= join_date.day <= 25:
                        mcount += 0.5
                    else:
                        mcount += 0 
            if mcount>0:
                today = date.today()
                if not frappe.db.exists('Leave Allocation',{'employee':e[0],'leave_type':'Earned Leave','from_date':["<=",today],'to_date':["<=",last_date_of_year],'docstatus':1}):
                    la = frappe.new_doc("Leave Allocation")
                    la.employee = e[0]
                    la.leave_type = "Earned Leave"
                    la.new_leaves_allocated = mcount*2
                    la.from_date = today
                    la.to_date = last_date_of_year
                    la.save(ignore_permissions=True)
                    la.submit()

@frappe.whitelist()        
def format_currency(value):
    if value is None:
        return "0"
    
    number_str = str(int(value))
    
    if len(number_str) > 3:
        last_three = number_str[-3:]  
        other_digits = number_str[:-3] 
        
        formatted_other = []
        while len(other_digits) > 2:
            formatted_other.append(other_digits[-2:])
            other_digits = other_digits[:-2]
        if other_digits:
            formatted_other.append(other_digits)        
        formatted_other.reverse()
        formatted_number = ','.join(formatted_other) + ',' + last_three
    else:
        formatted_number = number_str
    
    return formatted_number

# While cancel the documement Cancellation Remarks Mandatory  
@frappe.whitelist()
def cancellation_remarks_mandatory(doc, method):
      
    frappe.db.set_value("Admission", {"name": doc.name}, "cancel_remark", 1)
    
    if not doc.cancellation_remarks:
        frappe.throw("Please provide a reason for cancellation.")

# Validate Student Doctype
@frappe.whitelist()
def student_doc_validation_method(doc,method):
    if doc.name:
        if doc.custom_mobile_number_:
            phone_num = frappe.db.get_value('Student',{"custom_mobile_number_":doc.custom_mobile_number_,'name':['!=',doc.name],'enabled':1},'custom_mobile_number_')
            if phone_num:
                frappe.throw("Student Mobile Number already exists")
        # if doc.custom_guardian_phone_number:
        #     guardian_num = frappe.db.get_value('Student',{"custom_guardian_phone_number":doc.custom_guardian_phone_number,'name':['!=',doc.name],'enabled':1},'custom_guardian_phone_number')
        #     if guardian_num:
        #         frappe.msgprint(f"Student with Guardian Phone Number {doc.custom_guardian_phone_number} already exists.")
        # if doc.custom_mobile_number_:
        #     emergency_contact = frappe.db.get_value('Student',{"custom_emergency_contact_":doc.custom_emergency_contact_,'name':['!=',doc.name],'enabled':1},'custom_emergency_contact_')
        #     if emergency_contact:
        #         frappe.msgprint(f"Student with Emergency Contact Number {doc.custom_emergency_contact_} already exists.")
        
@frappe.whitelist()
def employee_doc_validation_method(doc,method):   
    if doc.cell_number and doc.name:
        phone_num = frappe.db.get_value('Employee',{"cell_number":doc.cell_number,'name':['!=',doc.name]},'cell_number')
        if phone_num:
            frappe.throw("Mobile Number already exists")   
    if doc.emergency_phone_number and doc.name:
        phone_num = frappe.db.get_value('Employee',{"emergency_phone_number":doc.emergency_phone_number,'name':['!=',doc.name]},'emergency_phone_number')
        if phone_num:
            frappe.throw("Emergency Phone Number already exis ts")    

# create program enrollment for the student automatically, once student document is inserted
@frappe.whitelist()
def create_enrollment(doc,method):
    sem=frappe.db.get_all("Academic Term",{'academic_year':doc.custom_academic_year,'program':doc.custom_program},['name'])
    for s in sem:
        if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':s.name,'program':doc.custom_program,'dostatus':1}):
            edate=frappe.db.get_value("Academic Term",{'name':s.name},['term_start_date'])
            enroll=frappe.new_doc("Program Enrollment")
            enroll.student=doc.name
            enroll.program=doc.custom_program
            enroll.academic_year=doc.custom_academic_year
            enroll.enrollment_date=edate
            enroll.academic_term=s.name
            enroll.student_category=doc.custom_student_category
            if not frappe.db.exists("Student Batch Name",{'batch_name':doc.custom_academic_year}):
                batch=frappe.new_doc('Student Batch Name')
                batch.batch_name=doc.custom_academic_year
                # batch.insert(ignore_permissions=True)
                batch.save(ignore_permissions=True)
                frappe.db.commit()
                batch=batch.name
            else:
                batch=frappe.db.get_value("Student Batch Name",{'batch_name':doc.custom_academic_year},['name'])
            enroll.student_batch_name=batch
            # enroll.insert(ignore_permissions=True)
            enroll.save(ignore_permissions=True)
            enroll.submit()
            frappe.db.commit()
            if not frappe.db.exists("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
                                              "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category}):
                new = frappe.new_doc("Student Group")
                new.academic_year = enroll.academic_year
                new.group_based_on = "Batch"
                sem_no=frappe.db.get_value("Academic Term",{'name':enroll.academic_term},['custom_semester'])
                new.student_group_name = enroll.academic_term + "-" + enroll.program + "-" + sem_no + "-" +enroll.student_category
                new.academic_term =enroll.academic_term
                new.program = enroll.program
                new.batch = enroll.student_batch_name
                new.student_category = enroll.student_category
                new.max_strength = 0
                
                new.append('students', {
                            "student": enroll.student,
                        })
                new.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                std_group = frappe.get_doc("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
                                                    "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category})
                
                std_group.append('students', {
                            "student": enroll.student,
                        })
                std_group.save(ignore_permissions=True)
                frappe.db.commit()


@frappe.whitelist()
def delete_query():
    frappe.db.sql("Delete  FROM `tabRegistration` WHERE docstatus = 2")

@frappe.whitelist()
def institute():
    students = frappe.get_all("Student", ["custom_current_academic_term", "name", "custom_institute_name"])
    for student in students:
        if frappe.db.exists("Fees", {"student": student.name}):
            print("true")
            frappe.db.set_value("Fees", {"student": student.name}, "custom_institute", student.custom_institute_name)



@frappe.whitelist()
def get_education_details_table_data(admission_number):
    admission_doc = frappe.get_doc("Admission", admission_number)
    datalist = []
    for row in admission_doc.edu_details:
        datalist.append({
            "qualification": row.qualification,
            "institution_name": row.institution_name,
            "university_name": row.university_name,
            "country": row.country,
            "state": row.state,
            "year_of_pass": row.year_of_pass,
            "reg_number": row.reg_number,
            "maximum_mark": row.maximum_mark,
            "mark_in_": row.mark_in_,
            "mark_scored": row.mark_scored,
            "class":row.class_class,
            "grade":row.grade

        })

    return datalist

@frappe.whitelist()
def update_student_number(doc,method):
    frappe.db.set_value("Admission",doc.custom_admission_number,"student",doc.name)

# @frappe.whitelist()
# def create_student_group(doc, method):
#     if not frappe.db.exists("Student Group", {"academic_year": doc.academic_year, "academic_term": doc.academic_term, 
#                                               "program": doc.program, "batch": doc.student_batch_name, "student_category": doc.student_category}):
#         frappe.log_error("academic_term", doc.academic_term)
#         new = frappe.new_doc("Student Group")
#         new.academic_year = doc.academic_year
#         new.group_based_on = "Batch"
#         new.student_group_name = doc.student_category + " " + doc.academic_year
#         new.academic_term =doc.academic_term
#         new.program = doc.program
#         new.batch = doc.student_batch_name
#         new.student_category = doc.student_category
#         new.max_strength = 0
        
#         new.append('students', {
#                     "student": doc.student,
#                 })
#         new.save(ignore_permissions=True)
#         frappe.db.commit()
#     else:
#         std_group = frappe.get_doc("Student Group", {"academic_year": doc.academic_year, "academic_term": doc.academic_term, 
#                                               "program": doc.program, "batch": doc.student_batch_name, "student_category": doc.student_category})
        
#         std_group.append('students', {
#                     "student": doc.student,
#                 })
#         std_group.save(ignore_permissions=True)
#         frappe.db.commit()
            
# Jinja method for admission Date of Course Commencement in admission print format
def add_suffix_to_date(date_obj):
    from datetime import date
    if isinstance(date_obj, date):
        day = date_obj.day
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{day}{suffix} {date_obj.strftime('%b %Y')}"
    return "Invalid Date"

@frappe.whitelist()
def get_fees_category_options(doctype, txt, searchfield, start, page_len, filters):
    fees = filters.get("fees") if filters else None
    fees = frappe.get_doc("Fees", fees)
    return [(row.fees_category,) for row in fees.components]

from frappe.utils import  formatdate,get_last_day, get_first_day, add_days
#Set default to date is based on given from date(Report filters)
@frappe.whitelist()
def get_to_date(from_date):
	return get_last_day(from_date)

# Enable the enabled check in admission and regsitration while disabled the student
@frappe.whitelist()
def update_enabled(ad_name,re_name):
    frappe.db.set_value("Admission", ad_name, "enabled", 1)
    frappe.db.set_value("Registration",re_name,"disabled", 1)
    frappe.db.commit()

# Disable the enabled check in admission and regsitration while enable the student
@frappe.whitelist()
def update_disabled(ad_name,re_name):
    frappe.db.set_value("Admission", ad_name, "enabled", 0)
    frappe.db.set_value("Registration",re_name,"disabled", 0)
    frappe.db.commit()



# @frappe.whitelist()
# def delete_test():
#     gl_entry=frappe.db.get_all("Prospectus",["name"])
#     gl_entry=frappe.db.get_all("Additional Fee",["name"])
    # gl_entry=frappe.db.get_all("Payment Ledger Entry",{"delinked":1},["name"])
    # gl_entry=frappe.db.get_all("GL Entry",{"is_cancelled":1},["name"])
    # ind=0
    # for i in gl_entry:
        # print(i.name)
        # ind+=1
        # frappe.delete_doc("Payment Ledger Entry",i.name)
        # frappe.delete_doc("Additional Fee",i.name)
        # frappe.delete_doc("GL Entry",i.name)
        # frappe.delete_doc("Prospectus",i.name)
    # print(ind)


@frappe.whitelist()
def ad_no():
    doc=frappe.db.get_value("Registration",{'name':'R-HAA-00866'},['docstatus'])
    print("Test")
    return doc

# Validate mail id in student
@frappe.whitelist()
def validate_mail(doc,method):
    if frappe.db.exists("Student",{"student_email_id":doc.student_email_id,'name':['!=',doc.name],"enabled":1}):
        frappe.throw("Student Email ID must be unique")
    if frappe.db.exists("Student",{"custom_registration_number":doc.custom_registration_number,'name':['!=',doc.name],"enabled":1}):
        frappe.throw("Student Registration Number must be unique")
    if frappe.db.exists("Student",{"custom_aadhar_number":doc.custom_aadhar_number,'name':['!=',doc.name],"enabled":1}) and doc.custom_aadhar_number is not None:
        frappe.throw("Student Aadhar Number must be unique")

# Method to updated age field in employees
@frappe.whitelist()
def calculate_age(date_format="%Y-%m-%d"):
    emp=frappe.db.get_all("Employee",{'status':'Active'},['date_of_birth','name'])
    for e in emp:
        dob_str=str(e.date_of_birth)
        dob = datetime.strptime(dob_str, date_format).date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        frappe.db.set_value("Employee",e.name,'custom_age',age)

# Method to updated age field in employees
@frappe.whitelist()
def update_age(name,date_format="%Y-%m-%d"):
    emp=frappe.db.get_all("Employee",{'name':name},['date_of_birth','name'])
    for e in emp:
        dob_str=str(e.date_of_birth)
        dob = datetime.strptime(dob_str, date_format).date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return {'age':age}

# def create_hooks_mark_ot():
#     job = frappe.db.exists('Scheduled Job Type', 'update_employee_age')
#     if not job:
#         sjt = frappe.new_doc("Scheduled Job Type")
#         sjt.update({
#             "method": 'hindustan.custom.calculate_age',
#             "frequency": 'Daily',
#         })
#         sjt.save(ignore_permissions=True)
@frappe.whitelist()
def create_checkins():
    serial_number_list=["A6FE191061322"]
    to_date = date.today()
    from_date = '2023-02-20'
    for serial in serial_number_list:
        url = "http://192.168.1.241:81//iclock/webapiservice.asmx?op=GetTransactionsLog"
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n  <soap:Body>\n    <GetTransactionsLog xmlns=\"http://tempuri.org/\">\n      <FromDate>%s </FromDate>\n      <ToDate>%s </ToDate>\n      <SerialNumber>%s</SerialNumber>\n      <UserName>essl</UserName>\n      <UserPassword>essl</UserPassword>\n    </GetTransactionsLog>\n  </soap:Body>\n</soap:Envelope>" % (from_date,to_date,serial)

        ET.headers = {
        'Content-Type': 'text/xml'
        }
        response = requests.request("POST", url, headers=ET.headers, data=payload)
        print(response)
        root=ET.fromstring(response.text)
        my_dict = xmltodict.parse(response.text)
        attlog = my_dict['soap:Envelope']['soap:Body']['GetTransactionsLogResponse']['strDataList']
        mylist = attlog.split('\n')
        frappe.log_error(title='at',message=mylist)
        for mydict in mylist:
            mytlist = mydict.split('\t')
            emp_id = mytlist[0]
            date_time = mytlist[1]
            urls = "http://139.5.188.247//api/method/hindustan.biometric_checkin.mark_checkin?employee=%s&time=%s&device_id=%s" % (emp_id,date_time,serial)
            headers = { 'Content-Type': 'application/json','Authorization': 'token 8865755f910b85c: dde82e0c5520cb2'}
            responses = requests.request('GET',urls,headers=headers,verify=False)
            res = json.loads(responses.text)

@frappe.whitelist()
def update_admission():
    frappe.db.set_value("Fees Collection",'EVE-FC-2025-00005','docstatus',2)
    
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

from hindustan.hindustan.doctype.fees_collection.fees_collection import get_payment_entry                     
@frappe.whitelist()
def create_fees_collection_for_registration(doc, methods):
    registration_number = frappe.db.get_value("Student", doc.student, "custom_registration_number")
    
    if frappe.db.exists("Registration", registration_number):
        registration = frappe.get_doc("Registration", registration_number)

        if registration.amount_paid > 0:  
            fc = frappe.new_doc("Fees Collection")
            fc.student = doc.student
            fc.program_enrollment = doc.program_enrollment
            fc.due_date = doc.due_date
            fc.fee_structure = doc.fee_structure
            fc.payment_mode = "Cash"
            fc.payment_date = registration.payment_date
            fc.fees = doc.name
            fc.automatic_creation = 1
            fc.academic_term = doc.academic_term
            fc.fee_schedule = doc.fee_schedule

            for row in doc.components:
                paying_amount = 0 
                
                if row.fees_category == "Registration Fee":
                    if registration.paid__payable_amount == registration.amount_paid:
                        paying_amount = registration.amount_paid
                    elif registration.paid__payable_amount > registration.amount_paid:
                        if registration.concession_applicability == 1:
                            paying_amount = registration.amount_paid
                        else:
                            paying_amount = registration.amount_paid

                fc.append('components', {
                    "fees_category": row.fees_category,
                    "amount": row.amount,
                    "amount_paid": 0.00,
                    "description": row.description,
                    "outstanding_amount": row.custom_outstanding_amount,
                    "paying_amount": paying_amount
                })

            fc.insert(ignore_permissions=True)
            fc.submit()
            payment_entry = get_payment_entry(
                dt="Fees", dn=fc.fees, party_type="Student", 
                payment_type="Receive", allocated=fc.paying_amount,
                docname=fc.name, fc_type="Fees Collection", fc_name=fc.name
            )
            payment_entry.insert(ignore_permissions=True)
            payment_entry.submit()


# create program enrollment for the student automatically, once student document is inserted
@frappe.whitelist()
def create_enrollment_test(doc,method):
    sem=frappe.db.get_all("Academic Term",{'academic_year':doc.custom_academic_year,'program':doc.custom_program},['name'])
    for s in sem:
        if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':s.name,'program':doc.custom_program,'dostatus':1}):
            edate=frappe.db.get_value("Academic Term",{'name':s.name},['term_start_date'])
            enroll=frappe.new_doc("Program Enrollment")
            enroll.student=doc.name
            enroll.program=doc.custom_program
            enroll.academic_year=doc.custom_academic_year
            enroll.enrollment_date=edate
            enroll.academic_term=s.name
            enroll.student_category=doc.custom_student_category
            if not frappe.db.exists("Student Batch Name",{'batch_name':doc.custom_academic_year}):
                batch=frappe.new_doc('Student Batch Name')
                batch.batch_name=doc.custom_academic_year
                # batch.insert(ignore_permissions=True)
                # batch.save(ignore_permissions=True)
                # frappe.db.commit()
                batch=batch.name
            else:
                batch=frappe.db.get_value("Student Batch Name",{'batch_name':doc.custom_academic_year},['name'])
            enroll.student_batch_name=batch
            # enroll.insert(ignore_permissions=True)
            # enroll.save(ignore_permissions=True)
            # enroll.submit()
            # frappe.db.commit()
            if not frappe.db.exists("Student Group", {"academic_year": doc.custom_academic_year, "academic_term": s.name, 
                                              "program": doc.custom_program, "batch": batch, "student_category": doc.custom_student_category}):
                new = frappe.new_doc("Student Group")
                new.academic_year = doc.custom_academic_year
                new.group_based_on = "Batch"
                new.student_group_name = doc.custom_academic_year + "-" + s.name
                new.academic_term =s.name
                new.program = doc.custom_program
                new.batch = batch
                new.student_category = doc.custom_student_category
                new.max_strength = 0
                
                new.append('students', {
                            "student": enroll.student,
                        })
                new.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                std_group = frappe.get_doc("Student Group", {"academic_year": doc.custom_academic_year, "academic_term": s.name, 
                                                    "program": doc.custom_program, "batch": batch, "student_category": enroll.student_category})
                
                std_group.append('students', {
                            "student": enroll.student,
                        })
                std_group.save(ignore_permissions=True)
                frappe.db.commit()
