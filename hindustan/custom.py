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
# #create or update the Overall Fee Structure on submitting the Fee Structure Document
# def create_update_overall_fee_structure(doc,method):
#     fee_structures=frappe.get_all("Fee Structure",{'program':doc.program,'student_category':doc.student_category,"academic_year":doc.academic_year,'docstatus':("!=",2)},['name'])
#     fee_data = {}
#     for fee_structure in fee_structures:
#         fee_stru = frappe.get_doc("Fee Structure", fee_structure.name)
#         for c in fee_stru.components:
#             if c.fees_category not in fee_data:
#                 fee_data[c.fees_category] = {f"sem_{i}": 0 for i in range(1, 9)}  

#             semester_key = f"sem_{fee_stru.custom_semester}" 
#             if semester_key in fee_data[c.fees_category]:
#                 fee_data[c.fees_category][semester_key] += c.amount 
#     grand_total = {f"sem_{i}": 0 for i in range(1, 9)}
#     if frappe.db.exists("Overall Fee Structure",{'program':doc.program,'student_category':doc.student_category,"academic_year":doc.academic_year}):
#         overall_fee_stru = frappe.get_doc("Overall Fee Structure",{'program':doc.program,'student_category':doc.student_category,"academic_year":doc.academic_year})
#         overall_fee_stru.set('fee_structure', [])
#         for category, sem_data in fee_data.items():
#             for sem_key, amount in sem_data.items():
#                 grand_total[sem_key] += amount
#             overall_fee_stru.append('fee_structure', {
#                 'fees_category': category,
#                 **sem_data  
#             })
#         overall_fee_stru.append('fee_structure', {
#             'fees_category': 'Total',
#             **grand_total,
#         })
#         overall_fee_stru.save(ignore_permissions=True)
#     else:
#         overall_fee_stru = frappe.new_doc("Overall Fee Structure")
#         overall_fee_stru.program = doc.program
#         overall_fee_stru.academic_year = doc.academic_year
#         overall_fee_stru.student_category=doc.student_category
#         for category, sem_data in fee_data.items():
#             for sem_key, amount in sem_data.items():
#                 grand_total[sem_key] += amount
#             overall_fee_stru.append('fee_structure', {
#                 'fees_category': category,
#                 **sem_data  
#             })
#         overall_fee_stru.append('fee_structure', {
#             'fees_category': 'Total',
#             **grand_total,
#         })
#         overall_fee_stru.save(ignore_permissions=True)
#         frappe.db.commit()
        
# # Creating student log while submitting the payment entry
# @frappe.whitelist()
# def create_student_log_on_payment(doc, method):
#     if doc.party_type == "Student":
#         sl = frappe.new_doc("Student Log")
#         sl.student = doc.party
#         for ref in doc.references:
#             if ref.reference_doctype == "Fees":
#                 fee = frappe.get_doc("Fees", ref.reference_name)
#                 sl.type = "Payment"
#                 sl.date = today()
#                 sl.academic_year = fee.academic_year
#                 sl.academic_term = fee.academic_term
#                 sl.program = fee.program
#                 sl.student_batch = fee.student_batch
#                 fee_name = ref.reference_name
#                 message = f"Amount &#8377; {doc.total_allocated_amount} paid against the Payment Entry - <b><a href='http://139.5.188.247/app/payment-entry/{doc.name}'>{doc.name} and Fees - <b><a href='http://139.5.188.247/app/fees/{fee_name}'>{fee_name}</b></b>"
#                 message += "<table>"
#                 message += """<tr>
#                                 <td><b>Fees Category</b></td>
#                                 <td><b>Description</b></td>
#                                 <td><b>Amount</b></td>
#                                 <td><b>Amount Paid</b></td>
#                                 <td><b>Balance</b></td>
#                             </tr>"""
#                 tot_paid = 0
#                 for comp in fee.components:
#                     balance = comp.amount - comp.custom_amount_paid
#                     tot_paid += comp.custom_amount_paid
#                     message += f"""<tr>
#                                     <td>{comp.fees_category}</td>
#                                     <td>{comp.description}</td>
#                                     <td>{comp.amount}</td>
#                                     <td>{comp.custom_amount_paid}</td>
#                                     <td>{balance}</td>
#                                 </tr>"""
#                 message += f"""<tr>
#                                     <td></td>
#                                     <td><b>Total</b></td>
#                                     <td><b>{fee.grand_total}</b></td>
#                                     <td><b>{tot_paid}</b></td>
#                                     <td><b>{fee.outstanding_amount}</b></td>
#                                 </tr>"""
#                 message += "</table>"
#                 sl.log = message
#                 sl.save()

# # Delete student log when cancelling the payment entry
# @frappe.whitelist()
# def delete_student_log_on_payment(doc, method):
#     student_log = frappe.db.sql("""SELECT name FROM `tabStudent Log` WHERE log LIKE '%s'"""%(f"%{doc.name}%"),as_dict=True)
#     if student_log:
#         sl = frappe.get_doc("Student Log", student_log[0].name)
#         sl.delete()

# # To get the total outstanding and total grand total
# @frappe.whitelist()
# def validate_outstanding_amount(doc, method):
#     grand_total = 0
#     outstanding = 0
#     for row in doc.components: 
#         out=row.amount - row.custom_amount_paid
#         row.custom_outstanding_amount= out
#         grand_total += row.amount
#         outstanding +=out
#     doc.grand_total = grand_total
#     doc.outstanding_amount = outstanding
#     doc.grand_total_in_words = money_in_words(grand_total)

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




import frappe
from datetime import datetime, date

@frappe.whitelist()
def allocate_leaves_automatically_el():
    employees = frappe.get_all(
        'Employee',
        filters={'status':"Active",'employment_type': 'Non - Teaching Staff'},
        fields=['name', 'employee', 'date_of_joining']
    )

    today = datetime.today().date()
    current_year = today.year
    earned_leave_per_month = 2  # For partial-year allocations

    for employee in employees:
        doj = employee.date_of_joining
        if not doj:
            continue

        doj = doj.date() if isinstance(doj, datetime) else doj
        one_year_complete = doj.replace(year=doj.year + 1)

        

        # Determine allocation period
        if one_year_complete < date(current_year, 1, 1):
            # Employee completed 1 year **before this year** → full year allocation
            from_date = date(current_year, 1, 1)
            to_date = date(current_year, 12, 31)
            earned_leave_allocation = 25  # Full year
        elif one_year_complete <= today:
            # Employee completes 1 year **during this year** → partial-year allocation
            from_date = one_year_complete
            to_date = date(current_year, 12, 31)

            # Calculate months remaining including the current month
            months_remaining = (to_date.month - from_date.month) + 1
            earned_leave_allocation = months_remaining * earned_leave_per_month

            # Adjust based on joining day
            joining_day = doj.day
            if joining_day < 10:
                earned_leave_allocation += 2
            elif 10 <= joining_day <= 20:
                earned_leave_allocation += 1
        else:
            # Employee not yet completed 1 year → skip
            frappe.log_error(
                title="Employee not yet eligible",
                message=f"Employee {employee.name} ({doj}) completes 1 year on {one_year_complete}, no allocation created."
            )
            continue

        # Get closing balance to add to allocation (if needed)
        closing_balance = get_closing_balance_new(employee.name, 'Earned Leave', f'{current_year}-01-01')
        total_allocation = min(50, closing_balance + earned_leave_allocation)

        # Check if allocation already exists
        existing_allocation = frappe.db.exists('Leave Allocation', {
            'employee': employee.name,
            'leave_type': 'Earned Leave',
            'from_date': from_date,
            'to_date': to_date,
            'docstatus': 1
        })

        if not existing_allocation:
            create_leave_allocation_new(employee.name, 'Earned Leave', current_year,
                                        total_allocation, from_date, to_date)
            frappe.logger().info(
                f"Leave Allocation created for {employee.name}: {from_date} → {to_date}, Total Leave = {total_allocation}"
            )



def create_scheduled_event():
	job = frappe.db.exists('Scheduled Job Type', 'allocate_leaves_automatically_cl')
	if not job:
		sjt = frappe.new_doc("Scheduled Job Type")
		sjt.update({
			"method": 'hindustan.custom.allocate_leaves_automatically_cl',
			"frequency": 'Cron',
			"cron_format": '55 23 * * *'
		})
		sjt.save(ignore_permissions=True)



import frappe
from datetime import datetime, date

@frappe.whitelist()
def allocate_leaves_automatically_cl():
    employees = frappe.get_all(
        'Employee',
        filters={'status':"Active"},  
        fields=['name', 'employee', 'date_of_joining']
    )

    today = datetime.today().date()
    current_year = today.year

    for employee in employees:
        doj = employee.date_of_joining
        if not doj:
            continue

        doj = doj.date() if isinstance(doj, datetime) else doj
        one_year_complete = doj.replace(year=doj.year + 1)

        if one_year_complete.year == current_year and one_year_complete <= today:
            first_half_start = one_year_complete
            first_half_end = date(current_year, 6, 30)
            second_half_start = date(current_year, 7, 1)
            second_half_end = date(current_year, 12, 31)
            allocated_first_half = 0
            july_from = date(current_year, 7, 1)

            allocation = frappe.get_all('Leave Allocation',
                filters={
                    'employee': employee['name'],  
                    'leave_type': 'Casual Leave',
                    'from_date': first_half_start,
                    'to_date': second_half_end,
                    'docstatus': 1
                },
                fields=['name', 'total_leaves_allocated']  
            )
            allocated_first_half = 0
            allocated_second_half = 0

            if first_half_start <= first_half_end:
                months_first_half = (first_half_end.month - first_half_start.month) + 1
                first_month_cl = 1 if first_half_start.day <= 15 else 0.5
                allocated_first_half = first_month_cl + max(months_first_half - 1, 0)

            if first_half_start <= second_half_end:
                second_half_actual_start = max(first_half_start, second_half_start)
                months_second_half = (second_half_end.month - second_half_actual_start.month) + 1
                first_month_second_half = 1 if second_half_actual_start.day <= 15 else 0.5
                allocated_second_half = first_month_second_half + max(months_second_half - 1, 0)
        

            

            if allocation and today == july_from:
                allocation_doc = frappe.get_doc('Leave Allocation', allocation[0].name)
                old_total = allocation_doc.total_leaves_allocated or 0


                total_cl = old_total + allocated_second_half

                allocation_doc.total_leaves_allocated = total_cl
                allocation_doc.new_leaves_allocated = total_cl
                allocation_doc.save(ignore_permissions=True)
                frappe.db.commit()

                frappe.logger().info(
                    f"{employee['name']}: Allocation updated , second half {allocated_second_half}, total {total_cl}"
                )

                
            else:
                total_cl = allocated_first_half
                create_leave_allocation_new(
                    employee['name'], 'Casual Leave', current_year,
                    total_cl, first_half_start, second_half_end
                )
                frappe.logger().info(
                    f"{employee['name']}: Allocation created Mar–Dec, first half {allocated_first_half}, second half {allocated_second_half}, total {total_cl}"
                )

   
        elif one_year_complete.year < current_year:
            jan_from = date(current_year, 1, 1)
            dec_to = date(current_year, 12, 31)
            july_from = date(current_year, 7, 1)

            existing_allocation = frappe.db.exists('Leave Allocation', {
                'employee': employee.name,
                'leave_type': 'Casual Leave',
                'from_date': jan_from,
                'to_date': dec_to,
                'docstatus': 1
            })
            if not existing_allocation:
                create_leave_allocation_new(employee.name, 'Casual Leave', current_year, 6, jan_from, dec_to)
                frappe.logger().info(f"{employee.name}: Jan–Dec {current_year} allocated (6 leaves)")

            elif today == july_from:
                allocation = frappe.get_all('Leave Allocation',
                    filters={
                        'employee': employee.name,
                        'leave_type': 'Casual Leave',
                        'from_date': jan_from,
                        'to_date': dec_to,
                        'docstatus': 1
                    },
                    fields=['name', 'total_leaves_allocated']
                )

                if allocation:
                    allocation_doc = frappe.get_doc('Leave Allocation', allocation[0].name)
                    allocation_name = allocation[0].name
                    old_total = allocation[0].total_leaves_allocated or 0
                    new_total = old_total + 6
                    allocation_doc.new_leaves_allocated = new_total
                    allocation_doc.total_leaves_allocated = new_total
                    allocation_doc.save(ignore_permissions=True)
                    frappe.db.commit()

                    frappe.logger().info(
                        f"{employee.name}: July update added 6 + unused (total now {new_total})"
                    )


        else:
            frappe.logger().info(f"{employee.name} not eligible yet. DOJ: {doj}, completes 1 year on {one_year_complete}")




# import frappe
# from datetime import datetime, date

# @frappe.whitelist()
# def allocate_leaves_automatically_cl():
#     employees = frappe.get_all(
#         'Employee',
#         filters={'name':"HR-EMP-00062"},
#         fields=['name', 'employee', 'date_of_joining']
#     )

#     today = datetime.today().date()
#     current_year = today.year

#     for employee in employees:
#         doj = employee.date_of_joining
#         if not doj:
#             continue

#         doj = doj.date() if isinstance(doj, datetime) else doj
#         one_year_complete = doj.replace(year=doj.year + 1)

#         # --- Employee completed 1 year before current year ---
#         if one_year_complete.year < current_year:
#             jan_from = date(current_year, 1, 1)
#             dec_to = date(current_year, 12, 31)
#             july_from = date(current_year, 7, 1)

#             # --- Check if Jan–Dec leave already exists ---
#             existing_allocation = frappe.db.exists('Leave Allocation', {
#                 'employee': employee.name,
#                 'leave_type': 'Casual Leave',
#                 'from_date': jan_from,
#                 'to_date': dec_to,
#                 'docstatus': 1
#             })
#             if not existing_allocation:
#                 create_leave_allocation_new(employee.name, 'Casual Leave', current_year, 6, jan_from, dec_to)
#                 frappe.logger().info(f"{employee.name}: Jan–Dec {current_year} allocated (6 leaves)")

#             elif today >= july_from:
#                 allocation = frappe.get_all('Leave Allocation',
#                     filters={
#                         'employee': employee.name,
#                         'leave_type': 'Casual Leave',
#                         'from_date': jan_from,
#                         'to_date': dec_to,
#                         'docstatus': 1
#                     },
#                     fields=['name', 'total_leaves_allocated']
#                 )

#                 if allocation:
#                     allocation_name = allocation[0].name
#                     old_total = allocation[0].total_leaves_allocated or 0

#                     used_leaves = frappe.db.sql("""
#                         SELECT SUM(leaves) FROM `tabLeave Ledger Entry`
#                         WHERE employee=%s AND leave_type=%s
#                         AND from_date BETWEEN %s AND %s
#                     """, (employee.name, 'Casual Leave', jan_from, date(current_year, 6, 30)))

#                     used_leaves = used_leaves[0][0] or 0

#                     unused = max(old_total - used_leaves, 0)

#                     new_total = old_total + 6 + unused

#                     frappe.db.set_value('Leave Allocation', allocation_name, 'total_leaves_allocated', new_total)
#                     frappe.db.commit()

#                     frappe.logger().info(
#                         f"{employee.name}: Added 6 + {unused} unused (from Jan-Jun) = {new_total} total"
#                     )


#         elif one_year_complete.year == current_year and one_year_complete <= today:
#             from_date = one_year_complete
#             to_date = date(current_year, 12, 31)
#             months_remaining = (to_date.month - from_date.month) + 1
#             per_month_leave = 1 if doj.day < 15 else 0.5
#             total_leaves = months_remaining * per_month_leave

#             if not frappe.db.exists('Leave Allocation', {
#                 'employee': employee.name,
#                 'leave_type': 'Casual Leave',
#                 'from_date': from_date,
#                 'to_date': to_date,
#                 'docstatus': 1
#             }):
#                 create_leave_allocation_new(employee.name, 'Casual Leave', current_year, total_leaves, from_date, to_date)
#                 frappe.logger().info(f"{employee.name}: {from_date}-{to_date} allocated ({total_leaves} leaves)")
#         else:
#             frappe.logger().info(f"{employee.name} not eligible yet. DOJ: {doj}, completes 1 year on {one_year_complete}")




def get_leave_used(employee, leave_type, from_date, to_date):
    used = frappe.db.sql("""
        SELECT SUM(total_leave_days)
        FROM `tabLeave Application`
        WHERE employee=%s AND leave_type=%s AND docstatus=1
        AND from_date >= %s AND to_date <= %s
    """, (employee, leave_type, from_date, to_date))[0][0]
    return used or 0


# --- Helper function to create leave allocation ---
def create_leave_allocation_new(employee, leave_type, year, total_leave, from_date, to_date):
    doc = frappe.new_doc("Leave Allocation")
    doc.employee = employee
    doc.leave_type = leave_type
    doc.from_date = from_date
    doc.to_date = to_date
    doc.new_leaves_allocated = total_leave
    doc.save(ignore_permissions=True)
    doc.submit()


# Helper: Get closing balance
def get_closing_balance_new(employee, leave_type, date_from):
    opening_balance = get_opening_balance(employee, leave_type, date_from)
    availed_leaves = get_availed_leaves(employee, leave_type, date_from)
    closing_balance = opening_balance - availed_leaves
    return closing_balance if closing_balance >= 0 else 0


# Helper: Create allocation
def create_leave_allocation_new(employee, leave_type, year, total_allocation, from_date, to_date):
    doc = frappe.new_doc('Leave Allocation')
    doc.employee = employee
    doc.leave_type = leave_type
    doc.from_date = from_date
    doc.to_date = to_date
    doc.new_leaves_allocated = total_allocation
    doc.docstatus = 1
    doc.save(ignore_permissions=True)





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
# import frappe
# @frappe.whitelist()
# def teaching_type(doc, method):
   
#     if doc.employment_type == 'Teaching Staff' and doc.status == 'Active':
       
#         existing_instructor = frappe.db.exists("Instructor", {"employee": doc.name})
        
#         if not existing_instructor:
           
#             instructor_doc = frappe.new_doc("Instructor")
#             instructor_doc.instructor_name = doc.employee_name
#             instructor_doc.employee = doc.name
#             instructor_doc.department = doc.department
#             instructor_doc.gender = doc.gender
#             instructor_doc.status = doc.status
#             instructor_doc.custom_institute_name = doc.custom_institute_name

#             instructor_doc.insert(ignore_permissions=True)

            
#             frappe.log_error(
#                 title="Instructor Created",
#                 message=f"Instructor document created for employee {doc.name}"
#             )


# @frappe.whitelist()
# def update_due_date(due,name):
#     frappe.db.set_value("Fees",name,'due_date',due)
#     # fee.reload()
#     return "OK"



# def leave_restriction_el_before(doc, method):
#     # when el is applied after an holiday and another leave application is present before the holiday, then it is restricted
#     if doc.leave_type=='Earned Leave':
#         from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
#         holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
#         previous_date = frappe.utils.add_days(from_date, -1)    
#         while True:
#             is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list,'holiday_date': previous_date.strftime('%Y-%m-%d')})
#             if not is_holiday:
#                 break      
#             previous_date = frappe.utils.add_days(previous_date, -1)   
#         # check any application present on previous day    
#         existing_leave_from = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name': ('!=', doc.name),
#             'from_date': previous_date.strftime('%Y-%m-%d'),
#             'leave_type': doc.leave_type,
#             'docstatus': ('!=', 2)
#         })
        
#         existing_leave_to = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name': ('!=', doc.name),
#             'to_date': previous_date.strftime('%Y-%m-%d'),
#             'leave_type': doc.leave_type,
#             'docstatus': ('!=', 2)
#         })
        
#         if existing_leave_from or existing_leave_to:
#             frappe.throw('Another leave application with leave leave type Earned Leave is found before the holiday.Kindly combine and put as single application')

# @frappe.whitelist()
# def leave_restriction_el_after(doc, method):
#     # when el is applied before an holiday and another leave application is present after the holiday, then it is restricted
#     if doc.leave_type=='Earned Leave':
#         to_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
#         holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
#         next_day = frappe.utils.add_days(to_date, 1)
#         while True:
#             is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': next_day.strftime('%Y-%m-%d')})
#             if not is_holiday:
#                 break
#             next_day = frappe.utils.add_days(next_day, 1)
#         # check any application present on next day    
#         existing_leave_from = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name':('!=', doc.name),
#             'from_date': next_day.strftime('%Y-%m-%d'),
#             'leave_type': doc.leave_type,
#             'docstatus': ('!=', 2)
#         })
#         existing_leave_to = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name':('!=', doc.name),
#             'to_date': next_day.strftime('%Y-%m-%d'),
#             'leave_type': doc.leave_type,
#             'docstatus': ('!=', 2)
#         })   
#         if existing_leave_from or existing_leave_to:
#             frappe.throw('Another leave application with leave leave type Earned Leave is found after the holiday.Kindly combine and put as single application')

# @frappe.whitelist()
# def leave_restriction_combining_after(doc, method):
#     # when el is applied before an holiday and another leave application is present after the holiday, then it is restricted
#     if doc.leave_type=='Earned Leave' or doc.leave_type=='Casual Leave':
#         to_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
#         holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
#         next_day = frappe.utils.add_days(to_date, 1)
#         while True:
#             is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': next_day.strftime('%Y-%m-%d')})
#             if not is_holiday:
#                 break
#             next_day = frappe.utils.add_days(next_day, 1)
#         # check any application present on next day   
#         if doc.leave_type=='Earned Leave':
#             lt='Casual Leave'
#         else:
#             lt='Earned Leave'
#         existing_leave_from = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name':('!=', doc.name),
#             'from_date': next_day.strftime('%Y-%m-%d'),
#             'leave_type': lt,
#             'docstatus': ('!=', 2)
#         })
#         existing_leave_to = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name':('!=', doc.name),
#             'to_date': next_day.strftime('%Y-%m-%d'),
#             'leave_type': lt,
#             'docstatus': ('!=', 2)
#         })   
#         if existing_leave_from or existing_leave_to:
#             frappe.throw(f"Not allowed to combine {lt} and {doc.leave_type}")

# def leave_restriction_combining_before(doc, method):
#     # when el is applied after an holiday and another leave application is present before the holiday, then it is restricted
#     if doc.leave_type=='Earned Leave' or doc.leave_type=='Casual Leave':
#         from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
#         holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
#         previous_date = frappe.utils.add_days(from_date, -1)    
#         while True:
#             is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list,'holiday_date': previous_date.strftime('%Y-%m-%d')})
#             if not is_holiday:
#                 break      
#             previous_date = frappe.utils.add_days(previous_date, -1)   
#         if doc.leave_type=='Earned Leave':
#             lt='Casual Leave'
#         else:
#             lt='Earned Leave'
#         existing_leave_from = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name': ('!=', doc.name),
#             'from_date': previous_date.strftime('%Y-%m-%d'),
#             'leave_type': lt,
#             'docstatus': ('!=', 2)
#         })
        
#         existing_leave_to = frappe.db.exists('Leave Application', {
#             'employee': doc.employee,
#             'name': ('!=', doc.name),
#             'to_date': previous_date.strftime('%Y-%m-%d'),
#             'leave_type': lt,
#             'docstatus': ('!=', 2)
#         })
#         if existing_leave_from or existing_leave_to:
#             frappe.throw(f"Not allowed to combine {lt} and {doc.leave_type}")

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

# @frappe.whitelist()        
# def format_currency(value):
#     if value is None:
#         return "0"
    
#     number_str = str(int(value))
    
#     if len(number_str) > 3:
#         last_three = number_str[-3:]  
#         other_digits = number_str[:-3] 
        
#         formatted_other = []
#         while len(other_digits) > 2:
#             formatted_other.append(other_digits[-2:])
#             other_digits = other_digits[:-2]
#         if other_digits:
#             formatted_other.append(other_digits)        
#         formatted_other.reverse()
#         formatted_number = ','.join(formatted_other) + ',' + last_three
#     else:
#         formatted_number = number_str
    
#     return formatted_number

# # While cancel the documement Cancellation Remarks Mandatory  
# @frappe.whitelist()
# def cancellation_remarks_mandatory(doc, method):
      
#     frappe.db.set_value("Admission", {"name": doc.name}, "cancel_remark", 1)
    
#     if not doc.cancellation_remarks:
#         frappe.throw("Please provide a reason for cancellation.")

# # Validate Student Doctype
# @frappe.whitelist()
# def student_doc_validation_method(doc,method):
#     if doc.name:
#         if doc.custom_mobile_number_:
#             phone_num = frappe.db.get_value('Student',{"custom_mobile_number_":doc.custom_mobile_number_,'name':['!=',doc.name],'enabled':1},'custom_mobile_number_')
#             if phone_num:
#                 frappe.throw("Student Mobile Number already exists")
#         # if doc.custom_guardian_phone_number:
#         #     guardian_num = frappe.db.get_value('Student',{"custom_guardian_phone_number":doc.custom_guardian_phone_number,'name':['!=',doc.name],'enabled':1},'custom_guardian_phone_number')
#         #     if guardian_num:
#         #         frappe.msgprint(f"Student with Guardian Phone Number {doc.custom_guardian_phone_number} already exists.")
#         # if doc.custom_mobile_number_:
#         #     emergency_contact = frappe.db.get_value('Student',{"custom_emergency_contact_":doc.custom_emergency_contact_,'name':['!=',doc.name],'enabled':1},'custom_emergency_contact_')
#         #     if emergency_contact:
#         #         frappe.msgprint(f"Student with Emergency Contact Number {doc.custom_emergency_contact_} already exists.")
        
# @frappe.whitelist()
# def employee_doc_validation_method(doc,method):   
#     if doc.cell_number and doc.name:
#         phone_num = frappe.db.get_value('Employee',{"cell_number":doc.cell_number,'name':['!=',doc.name]},'cell_number')
#         if phone_num:
#             frappe.throw("Mobile Number already exists")   
#     if doc.emergency_phone_number and doc.name:
#         phone_num = frappe.db.get_value('Employee',{"emergency_phone_number":doc.emergency_phone_number,'name':['!=',doc.name]},'emergency_phone_number')
#         if phone_num:
#             frappe.throw("Emergency Phone Number already exists")    

# create program enrollment for the student automatically, once student document is inserted
@frappe.whitelist()
def create_enrollment(doc,method):
    sem=frappe.db.get_all("Academic Term",{'academic_year':doc.custom_academic_year,'program':doc.custom_program},['name'])
    for s in sem:
        if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':s.name,'program':doc.custom_program,'docstatus':1}):
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
                                              "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category }):
                new = frappe.new_doc("Student Group")
                new.academic_year = enroll.academic_year
                new.group_based_on = "Batch"
                sem_no=frappe.db.get_value("Academic Term",{'name':enroll.academic_term},['custom_semester'])
                new.student_group_name = enroll.academic_term + "-" + enroll.program + "-" + sem_no + "-" +enroll.student_category + "-" + enroll.student_batch_name
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
def institute():
    students = frappe.get_all("Student", ["custom_current_academic_term", "name", "custom_institute_name"])
    for student in students:
        if frappe.db.exists("Fees", {"student": student.name}):
            print("true")
            frappe.db.set_value("Fees", {"student": student.name}, "custom_institute", student.custom_institute_name)



# @frappe.whitelist()
# def get_education_details_table_data(admission_number):
#     admission_doc = frappe.get_doc("Admission", admission_number)
#     datalist = []
#     for row in admission_doc.edu_details:
#         datalist.append({
#             "qualification": row.qualification,
#             "institution_name": row.institution_name,
#             "university_name": row.university_name,
#             "country": row.country,
#             "state": row.state,
#             "year_of_pass": row.year_of_pass,
#             "reg_number": row.reg_number,
#             "maximum_mark": row.maximum_mark,
#             "mark_in_": row.mark_in_,
#             "mark_scored": row.mark_scored,
#             "class":row.class_class,
#             "grade":row.grade

#         })

#     return datalist

# @frappe.whitelist()
# def update_student_number(doc,method):
#     frappe.db.set_value("Admission",doc.custom_admission_number,"student",doc.name)

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
            
# # Jinja method for admission Date of Course Commencement in admission print format
# def add_suffix_to_date(date_obj):
#     from datetime import date
#     if isinstance(date_obj, date):
#         day = date_obj.day
#         if 10 <= day % 100 <= 20:
#             suffix = "th"
#         else:
#             suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
#         return f"{day}{suffix} {date_obj.strftime('%b %Y')}"
#     return "Invalid Date"

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

# # Enable the enabled check in admission and regsitration while disabled the student
# @frappe.whitelist()
# def update_enabled(ad_name,re_name):
#     frappe.db.set_value("Admission", ad_name, "enabled", 1)
#     frappe.db.set_value("Registration",re_name,"disabled", 1)
#     frappe.db.commit()

# # Disable the enabled check in admission and regsitration while enable the student
# @frappe.whitelist()
# def update_disabled(ad_name,re_name):
#     frappe.db.set_value("Admission", ad_name, "enabled", 0)
#     frappe.db.set_value("Registration",re_name,"disabled", 0)
#     frappe.db.commit()



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

# # Validate mail id in student
# @frappe.whitelist()
# def validate_mail(doc,method):
#     if frappe.db.exists("Student",{"student_email_id":doc.student_email_id,'name':['!=',doc.name],"enabled":1}):
#         frappe.throw("Student Email ID must be unique")
#     if frappe.db.exists("Student",{"custom_registration_number":doc.custom_registration_number,'name':['!=',doc.name],"enabled":1}):
#         frappe.throw("Student Registration Number must be unique")
#     if frappe.db.exists("Student",{"custom_aadhar_number":doc.custom_aadhar_number,'name':['!=',doc.name],"enabled":1}) and doc.custom_aadhar_number is not None:
#         frappe.throw("Student Aadhar Number must be unique")

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
def update_age(date_format="%Y-%m-%d"):
    emp=frappe.db.get_all("Employee",{'status':'Active'},['date_of_birth','name'])
    for e in emp:
        dob_str=str(e.date_of_birth)
        dob = datetime.strptime(dob_str, date_format).date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        frappe.db.set_value("Employee",e.name,'custom_age',age)

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
        # my_dict = xmltodict.parse(response.text)
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

# @frappe.whitelist()
# def update_receiving_person(doc,method):
#     instructor_doc = frappe.new_doc("Receiving Person")
#     instructor_doc.is_student = 1
#     instructor_doc.student = doc.name
#     instructor_doc.person_name = doc.student_name
#     instructor_doc.insert(ignore_permissions=True)

# @frappe.whitelist()
# def rename_receiver(doc,method):
#     if doc.is_student==1:
#         frappe.rename_doc('Receiving Person',doc.name,doc.student,force=1)

# @frappe.whitelist()
# def validate_advance_payments(doc, methods):
#     registration_number= frappe.db.get_value("Student", doc.student, "custom_registration_number")
#     if frappe.db.exists("Registration", registration_number):
#         registration = frappe.get_doc("Registration", registration_number)
#         if registration.amount_paid > 0:
#             for row in doc.components:
#                 row.custom_amount_paid = 0
#                 if row.fees_category == "Registration Fee":
#                     if registration.concession_applicability == 1:    
#                         if registration.amount_paid <= registration.paid__payable_amount:
#                             row.amount -= registration.concession_amount
#                             row.custom_amount_paid = registration.amount_paid
#                     else:
#                         if registration.amount_paid <= registration.paid__payable_amount:
#                             row.custom_amount_paid = registration.amount_paid                                                                                

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



@frappe.whitelist()
def stu_group_update():
    student=frappe.db.get_all('Student',['*'])
    for doc in student:
        prog=frappe.db.get_all("Program Enrollment",{'student':doc.name},['student_batch_name'])
        for p in prog:
            batch=p.student_batch_name
    if not frappe.db.exists("Student Group", {"academic_year": doc.custom_academic_year, "academic_term": doc.custom_current_academic_term, "program": doc.custom_program, "batch": batch, "student_category": doc.custom_student_category}):
        new = frappe.new_doc("Student Group")
        new.academic_year = doc.custom_academic_year
        new.group_based_on = "Batch"
        sem_no=frappe.db.get_value("Academic Term",{'name':doc.custom_current_academic_term},['custom_semester'])
        new.student_group_name = doc.custom_current_academic_term + "-" + doc.custom_program + "-" + sem_no + "-" + doc.custom_student_category 
        new.academic_term =doc.custom_current_academic_term
        new.program = doc.custom_program
        new.batch = batch
        new.student_category = doc.custom_student_category
        new.max_strength = 0
        
        new.append('students', {
                    "student": doc.name,
                })
        new.save(ignore_permissions=True)
        frappe.db.commit()
    else:
        std_group=frappe.get_doc("Student Group", {"academic_year": doc.custom_academic_year, "academic_term": doc.custom_current_academic_term, "program": doc.custom_program, "batch": batch, "student_category": doc.custom_student_category})

        std_group.append('students', {
                    "student": doc.name,
                })
        std_group.save(ignore_permissions=True)
        frappe.db.commit()
# @frappe.whitelist()
# def update_earned_basic(doc,method):
#     ss=frappe.get_doc("Salary Slip",doc.name)
#     for i in ss.earnings:
#         if i.salary_component=='Basic':
#             ss.custom_earned_basic=i.amount
#     ss.save()
#     ss.reload()

@frappe.whitelist()
def update_names():
    docs=frappe.db.get_all('Student',{'name':['!=','']},['name','student_name'])
    # count=1
    for doc in docs:
        instructor_doc = frappe.new_doc("Receiving Person")
        instructor_doc.is_student = 1
        instructor_doc.student = doc.name
        instructor_doc.person_name = doc.student_name
        instructor_doc.insert(ignore_permissions=True)

# @frappe.whitelist()
# def update_student_docs(program,academic_year):
#     student_docs=frappe.db.get_all('Student',{'enabled':1,'custom_program':program},['name'])
#     for docs in student_docs:
#         doc=frappe.get_doc('Student',docs.name)
#         sem=frappe.db.get_all("Academic Term",{'academic_year':academic_year,'program':doc.custom_program},['name'])
#         for s in sem:
#             if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':s.name,'program':doc.custom_program,'docstatus':1}):
#                 edate=frappe.db.get_value("Academic Term",{'name':s.name},['term_start_date'])
#                 enroll=frappe.new_doc("Program Enrollment")
#                 enroll.student=doc.name
#                 enroll.program=doc.custom_program
#                 enroll.academic_year=academic_year
#                 enroll.enrollment_date=edate
#                 enroll.academic_term=s.name
#                 enroll.student_category=doc.custom_student_category
#                 if not frappe.db.exists("Student Batch Name",{'batch_name':doc.custom_academic_year}):
#                     # frappe.errprint("NOT Student Batch")
#                     batch=frappe.new_doc('Student Batch Name')
#                     batch.batch_name=doc.custom_academic_year
#                     # batch.insert(ignore_permissions=True)
#                     batch.save(ignore_permissions=True)
#                     frappe.db.commit()
#                     batch=batch.name
#                 else:
#                     # frappe.errprint("Student Batch")
#                     batch=frappe.db.get_value("Student Batch Name",{'batch_name':doc.custom_academic_year},['name'])
#                 enroll.student_batch_name=batch
#                 # enroll.insert(ignore_permissions=True)
#                 enroll.save(ignore_permissions=True)
#                 enroll.submit()
#                 frappe.db.commit()
#                 if not frappe.db.exists("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
#                                                 "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category}):
#                     # frappe.errprint("NOT Student group")
#                     new = frappe.new_doc("Student Group")
#                     new.academic_year = enroll.academic_year
#                     new.group_based_on = "Batch"
#                     sem_no=frappe.db.get_value("Academic Term",{'name':enroll.academic_term},['custom_semester'])
#                     new.student_group_name = enroll.academic_term + "-" + enroll.program + "-" + sem_no + "-" +enroll.student_category + "-" + enroll.student_batch_name
#                     new.academic_term =enroll.academic_term
#                     new.program = enroll.program
#                     new.batch = enroll.student_batch_name
#                     new.student_category = enroll.student_category
#                     new.max_strength = 0
                    
#                     new.append('students', {
#                                 "student": enroll.student,
#                             })
#                     new.save(ignore_permissions=True)
#                     frappe.db.commit()
#                     frappe.errprint(new)
#                 else:
#                     # frappe.errprint("NOT Student group")
#                     std_group = frappe.get_doc("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
#                                                         "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category})
#                     std_group.append('students', {
#                                 "student": enroll.student,
#                             })
#                     std_group.save(ignore_permissions=True)
#                     frappe.db.commit()
#     frappe.msgprint('Documents Updated')



# @frappe.whitelist()
# def check_academic_term(doc,method):
#     if frappe.db.exists("Academic Term",{'name':['!=',doc.name],'program':doc.program,'custom_semester':doc.custom_semester, 'academic_year': doc.academic_year}):
#         term=frappe.db.get_value("Academic Term",{'name':['!=',doc.name],'program':doc.program,'custom_semester':doc.custom_semester, 'academic_year': doc.academic_year},['name'])
#         form_link = get_link_to_form("Academic Term", term)
#         frappe.throw(f"Already another term present with same program and semester. {form_link}")

@frappe.whitelist()
def update_outstanding_amount():
    fdoc=frappe.get_doc('Fees','EVE-FEE-2025-01266')
    out=0
    for d in fdoc.components:
        out+=d.custom_outstanding_amount
        print(out)



# @frappe.whitelist()
# def change_user_permission(reports=None, name=None, user_id=None):
# 	"""
# 	Creates or deletes User Permission for Employee based on reports_to.
# 	- user_id can be empty for new employee; User Permission will be created later.
# 	"""

# 	# previous manager
# 	previous_manager = frappe.db.get_value("Employee", name, "reports_to")

# 	# Delete old permission if previous manager exists and has user_id
# 	if previous_manager:
# 		prev_user_id = frappe.db.get_value("Employee", {"name": previous_manager}, "user_id")
# 		if prev_user_id and user_id:
# 			existing = frappe.get_all(
# 				"User Permission",
# 				filters={
# 					"user": prev_user_id,
# 					"allow": "Employee",
# 					"for_value": name
# 				},
# 				fields=["name"]
# 			)
# 			for doc in existing:
# 				frappe.delete_doc("User Permission", doc.name, ignore_permissions=True)

# 	# Update reports_to1 in Employee table
# 	frappe.db.set_value("Employee", name, "reports_to", reports)

# 	# Create new permission only if reports_to and both user_ids exist
# 	if reports:
# 		manager_user = frappe.db.get_value("Employee", {"name": reports}, "user_id")
# 		if manager_user and user_id:
# 			existing = frappe.get_all(
# 				"User Permission",
# 				filters={
# 					"user": manager_user,
# 					"allow": "Employee",
# 					"for_value": name
# 				},
# 				fields=["name"]
# 			)
# 			if not existing:
# 				new = frappe.new_doc("User Permission")
# 				new.user = manager_user
# 				new.allow = "Employee"
# 				new.for_value = name
# 				new.hide_descendants = 1
# 				new.insert(ignore_permissions=True)
# 			return "created"
# 		else:
# 			# optional msg if manager has no user_id
# 			if not manager_user:
# 				frappe.msgprint(f"Reports To employee '{reports}' has no user_id yet")
# 			return "skipped"

# 	return "deleted"


# def employee_reports_to_permission(doc, method):
# 	"""
# 	This runs before save on Employee (manual or Data Import)
# 	"""

# 	# Call change_user_permission to create/delete User Permission
# 	change_user_permission(reports=doc.reports_to, name=doc.name, user_id=doc.user_id)


# def program_change_check(doc, method):

#     if not doc.student or not doc.academic_term:
#         return

#     student = frappe.get_doc("Student", doc.student)

#     if not student.custom_is_program_changed:
#         return

#     academic_semester = frappe.db.get_value("Academic Term",doc.academic_term,"custom_semester") or 0

#     changed_sem = student.custom_sem__batch_ or 0

#     condition_1 = (
#         student.custom_previous_program
#         and student.custom_previous_program == doc.program
#         and changed_sem >= academic_semester
#     )

#     condition_2 = (
#         student.custom_program
#         and student.custom_program == doc.program
#         and changed_sem < academic_semester
#     )

#     if condition_1 or condition_2:

#         for row in doc.components:
#             row.amount = 0
#             # row.custom_amount_paid = 0
#             # row.custom_outstanding_amount = 0

#         doc.custom_remarks = "Program Changed"

