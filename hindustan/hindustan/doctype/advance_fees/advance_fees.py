# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdvanceFees(Document):
	def validate(self):
		for row in self.advance_payment:
			row.balance_amount = row.received_amount - row.adjusted_amount
			if row.received_amount == row.adjusted_amount:
				row.adjusted = 1
			else:
				row.adjusted = 0
    
