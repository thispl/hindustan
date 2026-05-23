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
def update_student_docs(program,academic_year):
    student_docs=frappe.db.get_all('Student',{'enabled':1,'custom_program':program},['name'])
    for docs in student_docs:
        doc=frappe.get_doc('Student',docs.name)
        sem=frappe.db.get_all("Academic Term",{'academic_year':academic_year,'program':doc.custom_program},['name'])
        for s in sem:
            if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':s.name,'program':doc.custom_program,'docstatus':1}):
                edate=frappe.db.get_value("Academic Term",{'name':s.name},['term_start_date'])
                enroll=frappe.new_doc("Program Enrollment")
                enroll.student=doc.name
                enroll.program=doc.custom_program
                enroll.academic_year=academic_year
                enroll.enrollment_date=edate
                enroll.academic_term=s.name
                enroll.student_category=doc.custom_student_category
                if not frappe.db.exists("Student Batch Name",{'batch_name':doc.custom_academic_year}):
                    # frappe.errprint("NOT Student Batch")
                    batch=frappe.new_doc('Student Batch Name')
                    batch.batch_name=doc.custom_academic_year
                    # batch.insert(ignore_permissions=True)
                    batch.save(ignore_permissions=True)
                    frappe.db.commit()
                    batch=batch.name
                else:
                    # frappe.errprint("Student Batch")
                    batch=frappe.db.get_value("Student Batch Name",{'batch_name':doc.custom_academic_year},['name'])
                enroll.student_batch_name=batch
                # enroll.insert(ignore_permissions=True)
                enroll.save(ignore_permissions=True)
                enroll.submit()
                frappe.db.commit()
                if not frappe.db.exists("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
                                                "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category}):
                    # frappe.errprint("NOT Student group")
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
                    frappe.errprint(new)
                else:
                    # frappe.errprint("NOT Student group")
                    std_group = frappe.get_doc("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
                                                        "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category})
                    std_group.append('students', {
                                "student": enroll.student,
                            })
                    std_group.save(ignore_permissions=True)
                    frappe.db.commit()
    frappe.msgprint('Documents Updated')


@frappe.whitelist()
def check_academic_term(doc,method):
    if frappe.db.exists("Academic Term",{'name':['!=',doc.name],'program':doc.program,'custom_semester':doc.custom_semester, 'academic_year': doc.academic_year}):
        term=frappe.db.get_value("Academic Term",{'name':['!=',doc.name],'program':doc.program,'custom_semester':doc.custom_semester, 'academic_year': doc.academic_year},['name'])
        form_link = get_link_to_form("Academic Term", term)
        frappe.throw(f"Already another term present with same program and semester. {form_link}")

