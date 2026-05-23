# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today
from frappe.model.document import Document
from frappe.utils.data import date_diff, now_datetime, nowdate, today, add_days
from datetime import datetime

class Admission(Document):
    def validate(self):
        if self.aadhar_number:
            if frappe.db.exists("Student",{"custom_aadhar_number":self.aadhar_number,"enabled":("!=",0)}):
                frappe.throw("Invalid Aadhar Number")
            elif frappe.db.exists("Admission",{"aadhar_number":self.aadhar_number,'name':['!=',self.name],'docstatus':["!=",2],"enabled":0}):
                frappe.throw("Invalid Aadhar Number")
        if self.email_id:
            if frappe.db.exists("Student",{"student_email_id":self.email_id,"enabled":("!=",0)}):
                frappe.throw("Invalid Mail ID")
            elif frappe.db.exists("Admission",{"student_email_id":self.email_id,'name':['!=',self.name],'docstatus':["!=",2],"enabled":0}):
                frappe.throw("Invalid Mail ID")
        if self.phone_number and self.name:
            phone_num = frappe.db.get_value('Admission',{"phone_number":self.phone_number,'name':['!=',self.name],'docstatus':["!=",2],"enabled":0},'phone_number')
            if phone_num:
                frappe.throw("Phone number already exists")
        if self.guardian_phone_number and self.name:
            phone_num = frappe.db.get_value('Admission',{"guardian_phone_number":self.guardian_phone_number,'name':['!=',self.name],'docstatus':["!=",2],"enabled":0},'guardian_phone_number')
            if phone_num:
                frappe.msgprint("Guardian Phone number already assigned to the another Stuent")
        if self.emergency_contact and self.name:
            phone_num = frappe.db.get_value('Admission',{"emergency_contact":self.emergency_contact,'name':['!=',self.name],'docstatus':["!=",2],"enabled":0},'emergency_contact')
            if phone_num:
                frappe.msgprint("Emergency Contact Number already assigned to the another Stuent ")
    def on_submit(self):
        # Create Registraion from Admission
        if self.spot_admission==1:
            reg = frappe.new_doc("Registration")
            reg.spot_admission = self.spot_admission
            reg.excess_amount = 0
            reg.amount_paid = 0
            reg.institution_name = self.institution_name
            if self.aadhar_number is not None:
                reg.aadhar_number = self.aadhar_number
            reg.program = self.program
            reg.student_name = self.student_name
            reg.phone_number = self.phone_number
            reg.date = self.admission_date
            reg.father_name = self.father_name
            reg.gender = self.gender
            reg.date_of_birth = self.dob
            reg.student_category = self.student_category
            reg.academic_year = self.academic_year
            reg.academic_term = self.batch__semester
            reg.address = self.permanent_address
            frappe.db.commit()
            reg.save(ignore_permissions=True)
            self.registration_number = reg.name
            reg.submit()   
        # Create Student 
        if not frappe.db.exists('Student',{'custom_admission_number':self.name,'enabled':1}):
            if frappe.db.exists('Student',{"custom_mobile_number_":self.phone_number,'enabled':1}):
                frappe.throw(f"Student with phone number {self.phone_number} already exists.")
            if frappe.db.exists('Student',{"student_email_id":self.email_id,'enabled':1}):
                frappe.throw(f"Student with email ID {self.email_id} already exists.")
            if self.aadhar_number is not None:
                if frappe.db.exists('Student',{"custom_aadhar_number":self.aadhar_number,'enabled':1}):
                    frappe.throw(f"Student with Aadhar Number {self.aadhar_number} already exists.")
            if self.registration_number!=None:
                if frappe.db.exists('Student',{"custom_registration_number":self.registration_number,'enabled':1}):
                    frappe.throw(f"Student with Registration Number  {self.registration_number} already exists.")
            if frappe.db.exists('Student',{"custom_admission_number":self.name,'enabled':1}):
                frappe.throw(f"Student with Admission Number {self.name} already exists.")
            student=frappe.new_doc("Student")
            # Details
            student.custom_registration_number=self.registration_number
            student.custom_admission_number=self.name
            student.custom_student_category=self.student_category
            student.first_name=self.student_name
            student.date_of_birth=self.dob
            student.student_email_id=self.email_id
            student.custom_mobile_number_=self.phone_number
            student.custom_program=self.program
            student.gender=self.gender
            student.nationality=self.nationality
            # emergency_contact_num = self.emergency_contact.split("-")
            # guardian_phone_number = self.guardian_phone_number.split("-")
            # student.custom_emergency_contact_ = emergency_contact_num[1:2]
            # student.custom_guardian_phone_number = guardian_phone_number[1:2]
            # Institute Details
            student.custom_institute_name=self.institution_name
            student.custom_current_academic_term=self.batch__semester
            student.custom_academic_year=self.academic_year
            # Address
            student.country = self.country
            student.state = self.state
            student.city = self.district
            student.pin_code = self.pin_code
            student.save(ignore_permissions=True)
            frappe.db.commit()
            self.student = student.name
            
        # Advance Fee
        if self.registration_number and self.excess_amount > 0:
            advance_fees = frappe.db.exists("Advance Fees", {"registration_number": self.registration_number})
            if advance_fees:
                adv = frappe.get_doc("Advance Fees", {"registration_number": self.registration_number})
                adv.append('advance_payment', {
                    "reference_type": "Admission",
                    "reference_number": self.name,
                    "date": today(),
                    "received_amount": self.excess_amount,
                    "balance_amount": self.excess_amount
                })
                adv.save()
            else:
                adv = frappe.new_doc("Advance Fees")
                adv.registration_number = self.registration_number
                adv.append('advance_payment', {
                    "reference_type": "Admission",
                    "reference_number": self.name,
                    "date": today(),
                    "received_amount": self.excess_amount,
                })
                adv.save()
    def on_cancel(self):
        creation_tim = self.creation
        creation_time=datetime.strftime(creation_tim,'%Y-%m-%d %H:%M:%S')
        current_time = frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S')
        hours_difference = time_diff_in_hours(current_time, creation_time)
        if hours_difference > 48:
            frappe.throw("Cancellation is not allowed as the document is older than 48 hours.")
        if frappe.db.exists("Student",{"custom_admission_number":self.name}):
            student=frappe.get_doc("Student",{"custom_admission_number":self.name})
            program_enrolment=frappe.db.get_all("Program Enrollment",{"student":student.name},["name"])
            course_enrolment=frappe.db.get_all("Course Enrollment",{"student":student.name},["name"])
            for j in course_enrolment:
                course=frappe.get_doc("Course Enrollment",j)
                course.delete()
            for i in program_enrolment:
                program=frappe.get_doc("Program Enrollment",i)
                student_group=frappe.db.get_all("Student Group",{"academic_year":program.academic_year,"student_category":program.student_category,"batch":program.student_batch_name,"program":program.program},["name"])
                for m in student_group:
                    group=frappe.get_doc("Student Group",m)
                    group.students = [
                            row for row in group.students if row.student != program.student
                        ]
                    for idx, row in enumerate(group.students, start=1):
                        row.idx = idx
                    group.save()
                program.cancel()
                program.delete()

            student.delete()        
        # Remove Admission row from Advance Fees
        advance_fees = frappe.db.exists("Advance Fees", {"registration_number": self.registration_number})
        if advance_fees:
            adv = frappe.get_doc("Advance Fees", {"registration_number": self.registration_number})
            for row in adv.advance_payment:
                if row.reference_number == self.name:
                    adv.advance_payment.remove(row)
                    break
            adv.save()


def time_diff_in_hours(out_time_str, in_time_str):
    out_time = datetime.strptime(out_time_str, '%Y-%m-%d %H:%M:%S')
    in_time = datetime.strptime(in_time_str, '%Y-%m-%d %H:%M:%S')
    time_difference = out_time - in_time
    
    hours = time_difference.total_seconds() / 3600
    return round(hours)

def time_diff_in_minutes(out_time, in_time):
    if isinstance(out_time, str):
        out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(in_time, str):
        in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')

    time_difference = out_time - in_time
    minutes = time_difference.total_seconds() / 60
    return round(minutes)

    

@frappe.whitelist()
def get_fees_structure(academic_year, program, student_category, no_of_semesters):
    if no_of_semesters:
        no_of_semesters = int(no_of_semesters)
    # Fetch fee structure document
    fee_structure = frappe.db.exists("Overall Fee Structure", {
        'student_category': student_category,
        'program': program,
        'academic_year': academic_year,
        'no_of_semesters': no_of_semesters
    })

    if not fee_structure:
        data =[]
        return data
    else:
        fees_data = frappe.get_doc('Overall Fee Structure', {
            'student_category': student_category,
            'program': program,
            'academic_year': academic_year,
            'no_of_semesters': no_of_semesters
        })

        # Start HTML structure
        data = """
            <h4 class='text-center' style="color: black;">Fee Structure</h4>
            <div style="overflow-x: auto; color: black;">
            <table width='100%' class="text-center">
            <thead>
            <tr style="background-color: #ffe5b4; font-weight: 500; color: black;">
            <th width="10%" class="border border-1 border-dark">No.</th>
            <th width="40%" class="border border-1 border-dark"">Fees Category</th>
           """
        sem = []
        width = (50/no_of_semesters, 0)
        for idx in range(1, no_of_semesters + 1):
            data += f"""
                        <th width="{width}%" class="border border-1 border-dark">Sem {idx}</th>
                    """
            sem.append({
                f"sem{idx}": 0
            })
        data += """
                    </tr>
                    </thead>
                    <div>
                """
        doc = frappe.get_doc("Overall Fee Structure", fees_data.name)
        idx_row = 0
        grand_total = 0
        for row in doc.fee_structure:
            idx_row += 1
            # To make the total row bold
            if row.fees_category == "Total": 
                data += f"""
                            <tr style="font-weight: 700">
                            <td rowspan=2 class="border border-1 border-dark" style="text-align: center; font-weight: normal;">{idx_row}</td>
                            <td rowspan=2 class="border border-1 border-dark" style="text-align: left; padding-left: 10px; padding-right: 5px;">{row.fees_category}</td>
                        """
                for i in range(1, no_of_semesters + 1):
                    value = getattr(row, f"sem_{i}", 0)
                    data += f"""
                        <td class="border border-1 border-dark" style="text-align: right; padding-right: 10px;">
                        &#x20b9 {format_currency(value)}</td>
                    """
                    grand_total += value
                data += f"""
                            </tr>
                            <tr><td colspan={no_of_semesters} class="border border-1 border-dark" style="text-align: center; font-weight: 700">
                            &#x20b9 {format_currency(grand_total)}</td></tr>
                        """
            #  Not bold
            else:
                data += f"""
                            <tr>
                            <td class="border border-1 border-dark" style="text-align: center">{idx_row}</td>
                            <td class="border border-1 border-dark" style="text-align: left; padding-left: 10px; padding-right: 5px;">{row.fees_category}</td>
                        """
                for i in range(1, no_of_semesters + 1):
                    value = getattr(row, f"sem_{i}", 0)
                    data += f"""
                        <td class="border border-1 border-dark" style="text-align: right; padding-right: 10px;">
                        &#x20b9 {format_currency(value)}</td>
                    """
                data += "</tr>"
        return data



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


@frappe.whitelist()
def test_check():
    academic_year = "Test 2025-2028"
    program = "AME CAR147 B1.1/B2"
    student_category = "ALL"
    no_of_semesters = 5
    no_of_semesters = int(no_of_semesters)
    # Fetch fee structure document
    fee_structure = frappe.db.exists("Overall Fee Structure", {
        'student_category': student_category,
        'program': program,
        'academic_year': academic_year,
        'no_of_semesters': no_of_semesters
    })

    if not fee_structure:
        data =[]
        return data
    else:
        fees_data = frappe.get_doc('Overall Fee Structure', {
            'student_category': student_category,
            'program': program,
            'academic_year': academic_year,
            'no_of_semesters': no_of_semesters
        })

        # Start HTML structure
        data = """
            <h4 class='text-center' style="color: black;">Fee Structure</h4>
            <div style="overflow-x: auto; color: black;">
            <table width='100%' class="text-center">
            <thead>
            <tr style="background-color: #ffe5b4; font-weight: 500; color: black;">
            <th width="10%" class="border border-1 border-dark">No.</th>
            <th width="40%" class="border border-1 border-dark"">Fees Category</th>
           """
        sem = []
        width = (50/no_of_semesters, 0)
        for idx in range(1, no_of_semesters + 1):
            data += f"""
                        <th width="{width}%" class="border border-1 border-dark">Sem {idx}</th>
                    """
            sem.append({
                f"sem{idx}": 0
            })
        data += """
                    </tr>
                    </thead>
                    <div>
                """
        doc = frappe.get_doc("Overall Fee Structure", fees_data.name)
        idx_row = 0
        grand_total = 0
        for row in doc.fee_structure:
            idx_row += 1
            # To make the total row bold
            if row.fees_category == "Total": 
                data += f"""
                            <tr style="font-weight: 700">
                            <td rowspan=2 class="border border-1 border-dark" style="text-align: center; font-weight: normal;">{idx_row}</td>
                            <td rowspan=2 class="border border-1 border-dark" style="text-align: left; padding-left: 10px; padding-right: 5px;">{row.fees_category}</td>
                        """
                for i in range(1, no_of_semesters + 1):
                    value = getattr(row, f"sem_{i}", 0)
                    data += f"""
                        <td class="border border-1 border-dark" style="text-align: right; padding-right: 10px;">
                        &#x20b9 {format_currency(value)}</td>
                    """
                    grand_total += value
                data += f"""
                            </tr>
                            <tr><td colspan={no_of_semesters} class="border border-1 border-dark" style="text-align: center; font-weight: 700">
                            &#x20b9 {format_currency(grand_total)}</td></tr>
                        """
            #  Not bold
            else:
                data += f"""
                            <tr>
                            <td class="border border-1 border-dark" style="text-align: center">{idx_row}</td>
                            <td class="border border-1 border-dark" style="text-align: left; padding-left: 10px; padding-right: 5px;">{row.fees_category}</td>
                        """
                for i in range(1, no_of_semesters + 1):
                    value = getattr(row, f"sem_{i}", 0)
                    data += f"""
                        <td class="border border-1 border-dark" style="text-align: right; padding-right: 10px;">
                        &#x20b9 {format_currency(value)}</td>
                    """
                data += "</tr>"
        return data

import re
@frappe.whitelist()
def get_adm_no(ins, name):
    reg_list = frappe.db.get_all("Admission", {'institution_name': ins, 'name': ['!=', name], 'docstatus': ['!=', 2]}, ['admission_number'])
    max_num = 0
    pattern = re.compile(r"^A-(\w+)-(\d+)$")  
    for reg in reg_list:
        registration_number = reg['admission_number']
        match = pattern.match(registration_number)
        if match:
            num_part = int(match.group(2))
            if num_part > max_num:
                max_num = num_part    
    next_num = max_num + 1
    s_code = frappe.db.get_value('Institute', {'name': ins}, ['institute_short_code'])
    if next_num > 9999:
        next_reg_number = f'A-{s_code}-{str(next_num).zfill(5)}'
    else:
        next_reg_number = f'A-{s_code}-{next_num}'
    
    return next_reg_number
@frappe.whitelist()
def update_student_name(name,updated_name):
    if frappe.db.exists("Student",{'custom_admission_number':name}):
        stu=frappe.get_doc("Student",{'custom_admission_number':name})
        frappe.db.set_value('Student',stu.name,'student_name',updated_name)
        frappe.db.set_value('Student',stu.name,'first_name',updated_name)
        group=frappe.db.get_all("Student Group Student",{'parenttype':'Student Group','student':stu.name},['parent'])
        for g in group:
            student_group = frappe.get_doc("Student Group", g.parent)
            for row in student_group.students:
                if row.student == stu.name:
                    row.student_name = updated_name
                    row.flags.modified = True 
                    break  

            student_group.save(ignore_permissions=True)

        doc_list=['Fees','Program Enrollment','Fees Collection','Additional Fee','Advance Fees']
        for doc in doc_list:
            prog=frappe.db.get_all(doc,{'student':stu.name},['name'])
            for p in prog:
                frappe.db.set_value(doc,p.name,'student_name',updated_name)

