# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from datetime import date
from frappe.utils.data import add_days, add_years, today,getdate


class Prospectus(Document):
    def validate(self):
        if self.mobile_number and self.name:
            mobile_num = frappe.db.get_value('Prospectus',{"mobile_number":self.mobile_number,'name':['!=',self.name],'docstatus':["!=",2]},'mobile_number')
            if mobile_num:
                frappe.throw("Mobile number already exists")
    # def after_insert(self):
    #     doc_name = self.name
    #     split_doc_name = doc_name.split("-")
    #     if len(split_doc_name) > 1:
    #         receipt_number = "P" + "-".join(split_doc_name[1:2])
    #     self.receipt_number = receipt_number

    def on_submit(self):
        paid_amount = self.paid_amount
        if paid_amount > 0:
            student_name = self.student_name
            date = self.payment_date
            date_str = datetime.strptime(self.payment_date, "%Y-%m-%d") 
            formatted_date = date_str.strftime("%d-%m-%Y")
            if self.payment_mode:
                if self.payment_mode == 'Cash':
                    payment_mode = self.payment_mode 
                elif self.payment_mode == 'Cheque':
                    payment_mode = self.payment_mode 
                else:
                    payment_mode = 'Credit Card' 
            remarks = f"{student_name} paid an amount of {paid_amount} via {payment_mode} on {formatted_date}."
            # Create a new Journal Entry document
            journal_entry = frappe.new_doc('Journal Entry')
            journal_entry.voucher_type = 'Journal Entry'
            journal_entry.company = 'EVEHANS ACADEMY'
            journal_entry.posting_date = today()
            if payment_mode:
                journal_entry.mode_of_payment = payment_mode
            journal_entry.cheque_date = self.payment_date
            journal_entry.cheque_no  = self.name
            journal_entry.user_remark = remarks
            # Add rows to the Journal Entry Account child table
            journal_entry.append('accounts', {
                'account': 'Cash - EA', 
                'debit_in_account_currency': paid_amount,  
                'credit_in_account_currency': 0,    
            })

            journal_entry.append('accounts', {
                'account': 'Sales - EA', 
                'debit_in_account_currency': 0,    
                'credit_in_account_currency': paid_amount,  
            })

            # Save and submit the Journal Entry
            journal_entry.save()
            journal_entry.submit()
            frappe.db.set_value('Prospectus',self.name,'journal_entry_reference', journal_entry.name)

        else:
            frappe.throw("Kindly Pay the Prospectus Pay")

    # def before_cancel(self):
        # frappe.db.set_value('Prospectus',self.name,'cancel_remark', 1)
    def on_cancel(self):
        journal_entry_doc = frappe.get_doc('Journal Entry', self.journal_entry_reference)
        if journal_entry_doc:
            if journal_entry_doc.docstatus == 1:
                journal_entry_doc.cancel()
                frappe.db.set_value('Prospectus',self.name,'journal_entry_reference', '')


@frappe.whitelist()
def create_academic_year_doc_for_april_month():
    def is_apr_1(date_to_check):
        return date_to_check.month == 4 and date_to_check.day == 1
    date_to_check = date.today()
    if is_apr_1(date_to_check):
        current_year = date_to_check.year
        current_year = int(current_year)
        next_year = current_year + 1
        year_start_date =f"{current_year}-01-01"
        year_end_date = f"{current_year}-12-31"
        academic_year = f"{current_year}-{next_year}"
        if not frappe.db.exists("Academic Year", {'name': academic_year}):
            academic_year_doc = frappe.new_doc('Academic Year')
            academic_year_doc.academic_year_name = academic_year
            academic_year_doc.year_start_date = year_start_date
            academic_year_doc.year_end_date = year_end_date
            academic_year_doc.save(ignore_permissions=True)
            frappe.db.commit()

@frappe.whitelist()
def get_prospectus_fee(academic_year,program):
    prospectus_fee = frappe.db.get_value('Prospectus Fee',{'academic_year':academic_year,'program':program},['prospectus_fee'])
    if prospectus_fee:
        return prospectus_fee
    else: 
        return 'OK'

import re
@frappe.whitelist()
def get_rec_no():
    rec_list=frappe.db.get_all("Prospectus",{'receipt_number':['!=',''],'docstatus':['!=',2]},['receipt_number'])
    pattern = re.compile(r"^P\d{6}$")
    max_num = 0
    frappe.errprint("TEST")
    if rec_list:
        for rec in rec_list:
            receipt_number = rec['receipt_number']
            if pattern.match(receipt_number):
                num_part = int(receipt_number[1:]) 
                if num_part > max_num:
                    max_num = num_part
        new_receipt_number = f"P{str(max_num + 1).zfill(6)}"
    else:
        new_receipt_number='P000001'
    return new_receipt_number