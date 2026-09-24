# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.hr.utils import validate_active_employee
from hindustan.hindustan.doctype.fees_collection.fees_collection import update_outstanding_amount

class Concession(Document):
	# def on_submit(self):
	# 	if frappe.db.exists("Fees", self.fees):
	# 		fees = frappe.get_doc("Fees", self.fees)
	# 		fees.custom_concession = self.name
	# 		fees.custom_mark_concession = 1
	# 		fees.custom_concession_amount = self.concession_amount
	# 		fees.save(ignore_permissions=True)

	def on_submit(self):
		if frappe.db.exists("Fees", self.fees):
			fees = frappe.get_doc("Fees", self.fees)

			total_concession = frappe.db.sql(
				"""
				SELECT COALESCE(SUM(concession_amount), 0)
				FROM `tabConcession`
				WHERE fees = %s
				AND docstatus = 1
				""",
				(self.fees,),
			)[0][0]

			fees.custom_concession = self.name
			fees.custom_mark_concession = 1
			fees.custom_concession_amount = total_concession
			fees.save(ignore_permissions=True)
			update_outstanding_amount(fees.name)
	
	
	# def on_cancel(self):
	# 	if frappe.db.exists("Fees", self.fees):
	# 		fees = frappe.get_doc("Fees", self.fees)
	# 		fees.custom_concession = ""
	# 		fees.custom_mark_concession = 0
	# 		fees.custom_concession_amount = 0
	# 		fees.save(ignore_permissions=True)

	def on_cancel(self):
		if frappe.db.exists("Fees", self.fees):
			fees = frappe.get_doc("Fees", self.fees)

			total_concession = frappe.db.sql(
				"""
				SELECT COALESCE(SUM(concession_amount), 0)
				FROM `tabConcession`
				WHERE fees = %s
				AND docstatus = 1
				""",
				(self.fees,),
			)[0][0]

			fees.custom_concession = self.name if total_concession else ""
			fees.custom_mark_concession = 1 if total_concession else 0
			fees.custom_concession_amount = total_concession

			fees.save(ignore_permissions=True)
			update_outstanding_amount(fees.name)
   