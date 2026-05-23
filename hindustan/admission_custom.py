

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



# While cancel the documement Cancellation Remarks Mandatory  
@frappe.whitelist()
def cancellation_remarks_mandatory(doc, method):
      
    frappe.db.set_value("Admission", {"name": doc.name}, "cancel_remark", 1)
    
    if not doc.cancellation_remarks:
        frappe.throw("Please provide a reason for cancellation.")