
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






