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
    
# Validate mail id in student
@frappe.whitelist()
def validate_mail(doc,method):
    if frappe.db.exists("Student",{"student_email_id":doc.student_email_id,'name':['!=',doc.name],"enabled":1}):
        frappe.throw("Student Email ID must be unique")
    if frappe.db.exists("Student",{"custom_registration_number":doc.custom_registration_number,'name':['!=',doc.name],"enabled":1}):
        frappe.throw("Student Registration Number must be unique")
    if frappe.db.exists("Student",{"custom_aadhar_number":doc.custom_aadhar_number,'name':['!=',doc.name],"enabled":1}) and doc.custom_aadhar_number is not None:
        frappe.throw("Student Aadhar Number must be unique")

# create program enrollment for the student automatically, once student document is inserted
@frappe.whitelist()
def create_enrollment(doc,method):
    # sem=frappe.db.get_all("Academic Term",{'academic_year':doc.custom_academic_year,'program':doc.custom_program},['name'])
    # for s in sem:
    if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':doc.custom_current_academic_term,'program':doc.custom_program,'docstatus':1}):
        edate=frappe.db.get_value("Academic Term",{'name':doc.custom_current_academic_term},['term_start_date'])
        enroll=frappe.new_doc("Program Enrollment")
        enroll.student=doc.name
        enroll.program=doc.custom_program
        enroll.academic_year=doc.custom_academic_year
        enroll.enrollment_date=edate
        enroll.academic_term=doc.custom_current_academic_term
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
def update_student_number(doc,method):
    frappe.db.set_value("Admission",doc.custom_admission_number,"student",doc.name)



@frappe.whitelist()
def update_receiving_person(doc,method):
    instructor_doc = frappe.new_doc("Receiving Person")
    instructor_doc.is_student = 1
    instructor_doc.student = doc.name
    instructor_doc.person_name = doc.student_name
    instructor_doc.insert(ignore_permissions=True)
