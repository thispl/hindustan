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




def create_el():
	job = frappe.db.exists('Scheduled Job Type', 'allocate_leaves_automatically')
	if not job:
		sjt = frappe.new_doc("Scheduled Job Type")
		sjt.update({
			"method": 'hindustan.leave_all_custom.allocate_leaves_automatically',
			"frequency": 'Cron',
			"cron_format": '*/2 * * * *'
		})
		sjt.save(ignore_permissions=True)



def create_scheduled_event():
	job = frappe.db.exists('Scheduled Job Type', 'allocate_leaves_automatically_cl')
	if not job:
		sjt = frappe.new_doc("Scheduled Job Type")
		sjt.update({
			"method": 'hindustan.leave_all_custom.allocate_leaves_automatically_cl',
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
    print(employees)

    today = datetime.today().date()
    current_year = today.year

    for employee in employees:
        print("INSIDE")
        doj = employee.date_of_joining
        if not doj:
            continue

        doj = doj.date() if isinstance(doj, datetime) else doj
        one_year_complete = doj.replace(year=doj.year)
        print(doj)
        print(one_year_complete)
        if one_year_complete.year == current_year and one_year_complete <= today:
            print("INSIDE1")
            first_half_start = one_year_complete
            first_half_end = date(current_year, 6, 30)
            second_half_start = date(current_year, 7, 1)
            second_half_end = date(current_year, 12, 31)
            allocated_first_half = 0
            july_from = date(current_year, 7, 1)
            print(first_half_end)
            print(second_half_start)
            print(second_half_end)
            print(july_from)
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
            print(allocation)
            allocated_first_half = 0
            allocated_second_half = 0

            if first_half_start <= first_half_end:
                print("INSIDE11")
                months_first_half = (first_half_end.month - first_half_start.month) + 1
                first_month_cl = 1 if first_half_start.day <= 15 else 0.5
                allocated_first_half = first_month_cl + max(months_first_half - 1, 0)

            if first_half_start <= second_half_end:
                print("INSIDE12")
                second_half_actual_start = max(first_half_start, second_half_start)
                print(second_half_actual_start)
                months_second_half = (second_half_end.month - second_half_actual_start.month) + 1
                print(months_second_half)
                first_month_second_half = 1 if second_half_actual_start.day <= 15 else 0.5
                print(first_month_second_half)
                allocated_second_half = first_month_second_half + max(months_second_half - 1, 0)
                print(allocated_second_half)
        

            

            if allocation and today == july_from:
            # if allocation :
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
            print("INSIDE2")
            print(one_year_complete.year)
            print(current_year)
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
            print("INSIDE3")
            frappe.logger().info(f"{employee.name} not eligible yet. DOJ: {doj}, completes 1 year on {one_year_complete}")




def create_leave_allocation_new(employee, leave_type, year, total_leave, from_date, to_date):
    doc = frappe.new_doc("Leave Allocation")
    doc.employee = employee
    doc.leave_type = leave_type
    doc.from_date = from_date
    doc.to_date = to_date
    doc.new_leaves_allocated = total_leave
    doc.save(ignore_permissions=True)
    doc.submit()
