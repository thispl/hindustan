
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
  