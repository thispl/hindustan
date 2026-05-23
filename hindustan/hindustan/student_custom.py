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





