
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
def employee_doc_validation_method(doc,method):   
    if doc.cell_number and doc.name:
        phone_num = frappe.db.get_value('Employee',{"cell_number":doc.cell_number,'name':['!=',doc.name]},'cell_number')
        if phone_num:
            frappe.throw("Mobile Number already exists")   
    if doc.emergency_phone_number and doc.name:
        phone_num = frappe.db.get_value('Employee',{"emergency_phone_number":doc.emergency_phone_number,'name':['!=',doc.name]},'emergency_phone_number')
        if phone_num:
            frappe.throw("Emergency Phone Number already exists")