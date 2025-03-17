# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words
import datetime 
import frappe,erpnext
from frappe.utils import cint
import json
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
import re
class AdditionalFee(Document):
    def on_submit(self): 
        # Add the additional fee to the existing fee document of the student
        if frappe.db.exists("Fees", {
            'student': self.student,
            'academic_year': self.academic_year,
            'academic_term': self.academic_term,
            'program': self.program,
            'docstatus': ['!=', 2]
        }):
            fee_name = frappe.db.get_value("Fees", {
                'student': self.student,
                'academic_year': self.academic_year,
                'academic_term': self.academic_term,
                'program': self.program,
                'docstatus': ['!=', 2]
            }, ['name'])            
            
            if fee_name:
                fee = frappe.get_doc("Fees", fee_name)
                category_found = False
                for i in fee.components:
                    if i.fees_category == self.fee_category:
                        i.amount += self.amount
                        i.custom_amount_paid += 0
                        i.custom_outstanding_amount += self.amount
                        category_found = True
                if not category_found:
                    fee.append("components", {
                        'fees_category': self.fee_category,
                        'amount': self.amount,
                        'custom_amount_paid': '0',
                        'custom_outstanding_amount': self.amount
                    })

                fee.save()
                grand_total = 0.0
                amount_paid = 0.0
                for f in fee.components:
                    grand_total += float(f.amount)
                    amount_paid += float(f.custom_amount_paid)
                outstanding_amount = grand_total - amount_paid
                frappe.db.set_value("Fees", fee.name, 'grand_total', grand_total)
                frappe.db.set_value("Fees", fee.name, 'grand_total_in_words', money_in_words(grand_total))
                frappe.db.set_value("Fees", fee.name, 'outstanding_amount', outstanding_amount)
                journal = frappe.new_doc("Journal Entry")
                journal.voucher_type = 'Journal Entry'
                accounts = [
                    {
                        'account': 'Sales - EA',
                        'credit_in_account_currency': self.amount
                    },
                    {
                        'account': 'Cash - EA',
                        'debit_in_account_currency': self.amount,
                    }
                ]
                for account in accounts:
                    journal.append('accounts', account)
                journal.posting_date = today()
                journal.custom_additional_fee = self.name
                journal.save(ignore_permissions=True)
                frappe.db.commit()  
                journal.submit()
    # def before_cancel(self):
    #     if re.match(r'^\s*$',self.cancellation_remarks):
    #         frappe.throw("Please provide cancellation remarks before canceling the document.")
    #     if not self.cancellation_remarks:
    #         frappe.throw("Please provide cancellation remarks before canceling the document.")
    
    def on_cancel(self):
        
        if frappe.db.exists("Fees", {
            'student': self.student,
            'academic_year': self.academic_year,
            'academic_term': self.academic_term,
            'program': self.program,
            'docstatus': ['!=', 2]
        }):
            fee_name = frappe.db.get_value("Fees", {
                'student': self.student,
                'academic_year': self.academic_year,
                'academic_term': self.academic_term,
                'program': self.program,
                'docstatus': ['!=', 2]
            }, ['name'])            
            
            if fee_name:
                fee = frappe.get_doc("Fees", fee_name)
                for i in fee.components:
                    if i.fees_category == self.fee_category:
                        i.amount =i.amount - self.amount
                        i.custom_amount_paid += 0
                        i.custom_outstanding_amount -= self.amount
                        if i.amount == 0:
                            fee.components = [comp for comp in fee.components if comp != i]
                fee.save()
                grand_total = 0.0
                amount_paid = 0.0
                for f in fee.components:
                    grand_total += float(f.amount)
                    amount_paid += float(f.custom_amount_paid)
                outstanding_amount = grand_total - amount_paid
                frappe.db.set_value("Fees", fee.name, 'grand_total', grand_total)
                frappe.db.set_value("Fees", fee.name, 'grand_total_in_words', money_in_words(grand_total))
                frappe.db.set_value("Fees", fee.name, 'outstanding_amount', outstanding_amount)
        entry=frappe.db.get_value("Journal Entry",{'custom_additional_fee':self.name},['name'])
        if entry:
            journal=frappe.get_doc("Journal Entry",entry)
            journal.cancel()
        