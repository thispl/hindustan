# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils.data import add_days, add_years, today,getdate


class Registration(Document):
    def after_insert(self):
        if not self.receipt_number:
            rec_list=frappe.db.get_all("Registration",{'receipt_number':['!=',''],'docstatus':['!=',2]},['receipt_number'])
            pattern = re.compile(r"^R\d{6}$")
            max_num = 0
            if rec_list:
                for rec in rec_list:
                    receipt_number = rec['receipt_number']
                    if pattern.match(receipt_number):
                        num_part = int(receipt_number[1:]) 
                        if num_part > max_num:
                            max_num = num_part
                new_receipt_number = f"R{str(max_num + 1).zfill(6)}"
            else:
                new_receipt_number='R000001'
            self.receipt_number=new_receipt_number
        if not self.registration_number:
            count=frappe.db.count("Registration",{'institution_name':self.institution_name,'name':['!=',self.name],'docstatus':['!=',2]})
            count+=1
            s_code=frappe.db.get_value('Institute',{'name':self.institution_name},['institute_short_code'])
            reg_no = f'R-{s_code}-{str(count).zfill(5)}'
            self.registration_number=reg_no
    def validate(self):
        
        # if not self.receipt_number:
        #     frappe.errprint("test")
        #     doc_name = self.name
        #     split_doc_name = doc_name.split("-")
        #     if len(split_doc_name) > 2:
        #         frappe.errprint("test2")
        #         receipt_number = split_doc_name[-1].lstrip('0')
        #         receipt_number = "P" + receipt_number.zfill(6)
        #         frappe.errprint(receipt_number)
        #         self.receipt_number=receipt_number
        
        if self.phone_number and self.name:
            if frappe.db.exists('Registration',{"phone_number":self.phone_number,'name':['!=',self.name],'docstatus':["!=",2],"disabled":0}):
                mobile_num = frappe.db.get_value('Registration',{"phone_number":self.phone_number,'name':['!=',self.name],'docstatus':["!=",2],"disabled":0},'phone_number')
                if mobile_num:
                    frappe.throw("Phone number already exists")
    
    def on_submit(self):
        if self.excess_amount > 0:
            if frappe.db.exists("Advance Fees", {"registration_number": self.name}):
                adv = frappe.db.exists("Advance Fees", {"registration_number": self.name})
                adv.append("advance_payment", {
                    "reference_type": "Registration",
                    "reference_number": self.name,
                    "received_amount": self.excess_amount,
                    "balance_amount": self.excess_amount
                })
            else:
                adv = frappe.new_doc("Advance Fees")
                adv.registration_number = self.name
                adv.institution = self.institution_name
                adv.program = self.program
                adv.academic_year = self.academic_year
                adv.append("advance_payment", {
                    "reference_type": "Registration",
                    "reference_number": self.name,
                    "received_amount": self.excess_amount,
                    "balance_amount": self.excess_amount
                })
            adv.save(ignore_permissions = True)
        amount_paid = self.amount_paid
        if amount_paid > 0:
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
            remarks = f"{student_name} paid an amount of {amount_paid} via {payment_mode} on {formatted_date}."
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
                'debit_in_account_currency': amount_paid,  
                'credit_in_account_currency': 0,    
            })

            journal_entry.append('accounts', {
                'account': 'Sales - EA', 
                'debit_in_account_currency': 0,    
                'credit_in_account_currency': amount_paid,  
            })

            # Save and submit the Journal Entry
            journal_entry.save()
            journal_entry.submit()
            frappe.db.set_value('Registration',self.name,'journal_entry', journal_entry.name)
            frappe.db.set_value('Registration',self.name,'outstanding_amount_for_calculation',self.outstanding_amount)

        else:
            if self.spot_admission == 0:
                frappe.throw("Kindly Pay the Registration Fee")

    def on_update_after_submit(self):
        amount_paid = self.amount_paid
        payable_amount = self.paid__payable_amount
        if self.outstanding_amount_for_calculation > 0:
            if self.outstanding_amount_for_calculation < payable_amount:
                new_variable = payable_amount - self.outstanding_amount_for_calculation
            if amount_paid > new_variable:
                amount_paid = amount_paid - new_variable
        # if amount_paid > payable_amount:
            
        if amount_paid > 0 and self.outstanding_amount_for_calculation > 0:
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
            remarks = f"{student_name} paid an amount of {amount_paid} via {payment_mode} on {formatted_date}."
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
                'debit_in_account_currency': amount_paid,  
                'credit_in_account_currency': 0,    
            })

            journal_entry.append('accounts', {
                'account': 'Sales - EA', 
                'debit_in_account_currency': 0,    
                'credit_in_account_currency': amount_paid,  
            })

            # Save and submit the Journal Entry
            journal_entry.save()
            journal_entry.submit()
            frappe.db.set_value('Registration',self.name,'journal_entry', journal_entry.name)
            frappe.db.set_value('Registration',self.name,'outstanding_amount_for_calculation',self.outstanding_amount)

    def on_cancel(self):
        frappe.db.set_value('Registration',self.name,'cancel_remark', 1)
        if self.journal_entry:
            journal_entry_doc = frappe.get_doc('Journal Entry', self.journal_entry)
            if journal_entry_doc and self.cancellation_remarks:
                if journal_entry_doc.docstatus == 1:
                    journal_entry_doc.cancel()
                    frappe.db.set_value('Registration',self.name,'journal_entry', '')
        
            
@frappe.whitelist()
def get_reg_amount(sem,category,year,program):
    if frappe.db.exists("Fee Structure",{'program':program,'academic_year':year,'academic_term':sem,'student_category':category,'docstatus':1}):
        fee=frappe.get_doc("Fee Structure",{'program':program,'academic_year':year,'academic_term':sem,'student_category':category,'docstatus':1})
        for f in fee.components:
           if f.fees_category == 'Registration Fee':
               return f.amount
           
@frappe.whitelist()
def get_reg_no(ins,name):
    count=frappe.db.count("Registration",{'institution_name':ins,'name':['!=',name],'docstatus':['!=',2]})
    count+=1
    s_code=frappe.db.get_value('Institute',{'name':ins},['institute_short_code'])
    receipt_number = f'R-{s_code}-{str(count).zfill(5)}'
    return receipt_number
import re
@frappe.whitelist()
def get_rec_no():
    rec_list=frappe.db.get_all("Registration",{'receipt_number':['!=',''],'docstatus':['!=',2]},['receipt_number'])
    pattern = re.compile(r"^R\d{6}$")
    max_num = 0
    if rec_list:
        for rec in rec_list:
            receipt_number = rec['receipt_number']
            if pattern.match(receipt_number):
                num_part = int(receipt_number[1:]) 
                if num_part > max_num:
                    max_num = num_part
        new_receipt_number = f"R{str(max_num + 1).zfill(6)}"
    else:
        new_receipt_number='R000001'
    return new_receipt_number