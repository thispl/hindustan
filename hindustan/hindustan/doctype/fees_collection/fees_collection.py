# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import erpnext
import frappe
from erpnext.accounts.doctype.payment_request.payment_request import (
	make_payment_request,
)
from frappe.utils import today
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from functools import reduce
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe import _
from frappe.utils import money_in_words
from frappe.utils.csvutils import getlink
from frappe import ValidationError, _, qb, scrub, throw


class FeesCollection(AccountsController):
	def set_indicator(self):
		"""Set indicator for portal"""
		if self.outstanding_amount > 0:
			self.indicator_color = "orange"
			self.indicator_title = _("Unpaid")
		else:
			self.indicator_color = "green"
			self.indicator_title = _("Paid")

	def validate(self):
		self.calculate_total()
		self.set_missing_accounts_and_fields()
		self.validate_enrollment()
		validate_paying_amount(self)
		validate_excess_amount(self)

	def set_missing_accounts_and_fields(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().company
		if not self.currency:
			self.currency = erpnext.get_company_currency(self.company)
		if not (self.receivable_account and self.income_account and self.cost_center):
			accounts_details = frappe.get_all(
				"Company",
				fields=["default_receivable_account", "default_income_account", "cost_center"],
				filters={"name": self.company},
			)[0]
		if not self.receivable_account:
			self.receivable_account = accounts_details.default_receivable_account
		if not self.income_account:
			self.income_account = accounts_details.default_income_account
		if not self.cost_center:
			self.cost_center = accounts_details.cost_center
		if not self.contact_email:
			self.contact_email = self.get_student_emails()

	def validate_enrollment(self):
		enrollment_student = frappe.db.get_value(
			"Program Enrollment", self.program_enrollment, "student"
		)
		if enrollment_student != self.student:
			frappe.throw(
				_("Invalid Enrollment {0} for student {1}").format(
					frappe.bold(self.program_enrollment), frappe.bold(self.student)
				)
			)

	def get_student_emails(self):
		student_emails = frappe.db.sql_list(
			"""
			select g.email_address
			from `tabGuardian` g, `tabStudent Guardian` sg
			where g.name = sg.guardian and sg.parent = %s and sg.parenttype = 'Student'
			and ifnull(g.email_address, '')!=''
		""",
			self.student,
		)

		student_email_id = frappe.db.get_value("Student", self.student, "student_email_id")
		if student_email_id:
			student_emails.append(student_email_id)
		if student_emails:
			return ", ".join(list(set(student_emails)))
		else:
			return None

	def calculate_total(self):
		"""Calculates total amount."""
		self.grand_total = 0
		self.outstanding = 0
		for d in self.components:
			self.outstanding += d.outstanding_amount
			self.grand_total += d.amount
		self.grand_total_in_words = money_in_words(self.grand_total)

	def on_submit(self):
		udpate_advance_payment_on_master(self)
		update_advance_fees(self)
		fees = frappe.get_doc("Fees", self.fees)
		out=0
		for i in fees.components:
			out+=i.custom_outstanding_amount
		fees.custom_outstanding_amount=out
		fees.save(ignore_permissions=True)
		
		# self.make_gl_entries()
   
		if self.send_payment_request and self.contact_email:
			pr = make_payment_request(
				party_type="Student",
				party=self.student,
				dt="Fees",
				dn=self.name,
				recipient_id=self.contact_email,
				submit_doc=True,
				use_dummy_message=True,
			)
			frappe.msgprint(
				_("Payment request {0} created").format(getlink("Payment Request", pr.name))
			)
			

	def on_update(self):
		fees = frappe.get_doc("Fees", self.fees)
		tot = 0
		for row in fees.components:
			tot += row.custom_outstanding_amount
		frappe.db.set_value("Fees", fees.name, "outstanding_amount", tot)
	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
		cancel_fees_collection(self)
  
	def make_gl_entries(self):
		if not self.grand_total:
			return
		student_gl_entries = self.get_gl_dict(
			{
				"account": self.receivable_account,
				"party_type": "Student",
				"party": self.student,
				"against": self.income_account,
				"debit": self.grand_total,
				"debit_in_account_currency": self.grand_total,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
			},
			item=self,
		)

		fee_gl_entry = self.get_gl_dict(
			{
				"account": self.income_account,
				"against": self.student,
				"credit": self.grand_total,
				"credit_in_account_currency": self.grand_total,
				"cost_center": self.cost_center,
			},
			item=self,
		)

		from erpnext.accounts.general_ledger import make_gl_entries

		make_gl_entries(
			[student_gl_entries, fee_gl_entry],
			cancel=(self.docstatus == 2),
			update_outstanding="No",
			merge_entries=False,
		)

	def before_submit(self):
		validate_amount_paid(self)
		update_concession_on_paying_amount(self)
		create_concession(self)
		update_paid_amount(self)
		total_of_all_ammounts(self)
		

def get_fee_list(
	doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"
):
	user = frappe.session.user
	student = frappe.db.sql(
		"select name from `tabStudent` where student_email_id= %s", user
	)
	if student:
		return frappe.db.sql(
			"""
			select name, program, due_date, grand_total - outstanding_amount as paid_amount,
			outstanding_amount, grand_total, currency
			from `tabFees`
			where student= %s and docstatus=1
			order by due_date asc limit {0} , {1}""".format(
				limit_start, limit_page_length
			),
			student,
			as_dict=True,
		)


def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		"no_breadcrumbs": True,
		"title": _("Fees"),
		"get_list": get_fee_list,
		"row_template": "templates/includes/fee/fee_row.html",
	}

 
@frappe.whitelist()
def get_fee_components(fee_structure):
	if fee_structure:
		fs = frappe.get_all(
			"Fee Component",
			fields=["fees_category", "description", "amount", "custom_amount_paid", "custom_outstanding_amount"],
			filters={"parent": fee_structure},
			order_by="idx",
		)
		return fs

# Create Payment Entry
from erpnext.accounts.doctype.payment_entry.payment_entry import (
	set_party_type, set_party_account,set_party_account_currency, 
	set_payment_type,  
	get_bank_cash_account, get_party_bank_account, 
	set_paid_amount_and_received_amount, apply_early_payment_discount, 
	get_reference_as_per_payment_terms, update_accounting_dimensions, 
	split_early_payment_discount_loss, set_pending_discount_loss, 
	allocate_open_payment_requests_to_references
	)
@frappe.whitelist()
def get_payment_entry(
	dt,
	dn,
	fc_type, 
	fc_name,
	party_amount=None,
	bank_account=None,
	bank_amount=None,
	party_type=None,
	payment_type=None,
	reference_date=None,
	ignore_permissions=False,
	created_from_payment_request=False,
	allocated=None,
	docname=None,
):
	doc = frappe.get_doc(dt, dn)
	fc = frappe.get_doc(fc_type, fc_name)
	over_billing_allowance = frappe.db.get_single_value("Accounts Settings", "over_billing_allowance")
	if dt in ("Sales Order", "Purchase Order") and flt(doc.per_billed, 2) >= (100.0 + over_billing_allowance):
		frappe.throw(_("Can only make payment against unbilled {0}").format(_(dt)))

	if not party_type:
		party_type = set_party_type(dt)

	party_account = set_party_account(dt, dn, doc, party_type)
	party_account_currency = set_party_account_currency(dt, party_account, doc)

	if not payment_type:
		payment_type = set_payment_type(dt, doc)

	grand_total, outstanding_amount = set_grand_total_and_outstanding_amount(
		party_amount, dt, party_account_currency, doc
	)

	# bank or cash
	bank = get_bank_cash_account(doc, bank_account)

	# if default bank or cash account is not set in company master and party has default company bank account, fetch it
	if party_type in ["Customer", "Supplier"] and not bank:
		party_bank_account = get_party_bank_account(party_type, doc.get(scrub(party_type)))
		if party_bank_account:
			account = frappe.db.get_value("Bank Account", party_bank_account, "account")
			bank = get_bank_cash_account(doc, account)

	paid_amount, received_amount = set_paid_amount_and_received_amount(
		dt, party_account_currency, bank, outstanding_amount, payment_type, bank_amount, doc
	)

	reference_date = getdate(reference_date)
	paid_amount, received_amount, discount_amount, valid_discounts = apply_early_payment_discount(
		paid_amount, received_amount, doc, party_account_currency, reference_date
	)
	if fc.mark_concession and fc.concession_amount > 0 and fc.concession_on:
		paid_amount = fc.grand_total
	paid_amount = fc.grand_total
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = payment_type
	pe.company = doc.company
	pe.cost_center = doc.get("cost_center")
	pe.posting_date = nowdate()
	pe.reference_date = reference_date
	pe.mode_of_payment = fc.payment_mode
	if fc.payment_mode == "Cheque":
		pe.reference_no = fc.cheque_number
	if fc.payment_mode == "DD":
		pe.reference_no = fc.account_number
	if fc.payment_mode in ["Online Transfer", "GPAY / QR Code"]:
		pe.reference_no = fc.reference_number
	pm = frappe.get_doc("Mode of Payment", fc.payment_mode)
	for i in pm.accounts:
		if i.company == doc.company:
			pe.paid_to = i.default_account
	pe.party_type = party_type
	pe.party = doc.get(scrub(party_type))
	pe.contact_person = doc.get("contact_person")
	pe.contact_email = doc.get("contact_email")
	pe.ensure_supplier_is_not_blocked()
	pe.custom_reference_docname = docname

	pe.paid_from = party_account if payment_type == "Receive" else bank.account
	pe.paid_from_account_currency = (
		party_account_currency if payment_type == "Receive" else bank.account_currency
	)
	pe.paid_to_account_currency = party_account_currency if payment_type == "Pay" else bank.account_currency
	pe.paid_amount = paid_amount
	pe.received_amount = received_amount
	pe.letter_head = doc.get("letter_head")

	if dt in ["Purchase Order", "Sales Order", "Sales Invoice", "Purchase Invoice"]:
		pe.project = doc.get("project") or reduce(
			lambda prev, cur: prev or cur, [x.get("project") for x in doc.get("items")], None
		)  # get first non-empty project from items

	if pe.party_type in ["Customer", "Supplier"]:
		bank_account = get_party_bank_account(pe.party_type, pe.party)
		pe.set("bank_account", bank_account)
		pe.set_bank_account_data()

	# only Purchase Invoice can be blocked individually
	if doc.doctype == "Purchase Invoice" and doc.invoice_is_blocked():
		frappe.msgprint(_("{0} is on hold till {1}").format(doc.name, doc.release_date))
	else:
		if doc.doctype in (
			"Sales Invoice",
			"Purchase Invoice",
			"Purchase Order",
			"Sales Order",
		) and frappe.get_cached_value(
			"Payment Terms Template",
			doc.payment_terms_template,
			"allocate_payment_based_on_payment_terms",
		):
			for reference in get_reference_as_per_payment_terms(
				doc.payment_schedule, dt, dn, doc, grand_total, outstanding_amount, party_account_currency
			):
				pe.append("references", reference)
		else:
			if dt == "Dunning":
				for overdue_payment in doc.overdue_payments:
					pe.append(
						"references",
						{
							"reference_doctype": "Sales Invoice",
							"reference_name": overdue_payment.sales_invoice,
							"payment_term": overdue_payment.payment_term,
							"due_date": overdue_payment.due_date,
							"total_amount": overdue_payment.outstanding,
							"outstanding_amount": overdue_payment.outstanding,
							"allocated_amount": overdue_payment.outstanding,
						},
					)

				pe.append(
					"deductions",
					{
						"account": doc.income_account,
						"cost_center": doc.cost_center,
						"amount": -1 * doc.dunning_amount,
						"description": _("Interest and/or dunning fee"),
					},
				)
			else:
				pe.append(
					"references",
					{
						"reference_doctype": dt,
						"reference_name": dn,
						"bill_no": doc.get("bill_no"),
						"due_date": doc.get("due_date"),
						"total_amount": grand_total,
						"outstanding_amount": outstanding_amount,
						"allocated_amount": allocated,
					},
				)

	pe.setup_party_account_field()
	pe.set_missing_values()
	pe.set_missing_ref_details()

	update_accounting_dimensions(pe, doc)

	if party_account and bank:
		pe.set_exchange_rate(ref_doc=doc)
		pe.set_amounts()

		if discount_amount:
			base_total_discount_loss = 0
			if frappe.db.get_single_value("Accounts Settings", "book_tax_discount_loss"):
				base_total_discount_loss = split_early_payment_discount_loss(pe, doc, valid_discounts)

			set_pending_discount_loss(
				pe, doc, discount_amount, base_total_discount_loss, party_account_currency
			)

		pe.set_difference_amount()

	# If PE is created from PR directly, then no need to find open PRs for the references
	if not created_from_payment_request:
		allocate_open_payment_requests_to_references(pe.references, pe.precision("paid_amount"))

	return pe

@frappe.whitelist()
def set_grand_total_and_outstanding_amount(party_amount, dt, party_account_currency, doc):
	grand_total = outstanding_amount = 0
	if party_amount:
		grand_total = outstanding_amount = party_amount
	elif dt in ("Sales Invoice", "Purchase Invoice"):
		if party_account_currency == doc.company_currency:
			grand_total = doc.base_rounded_total or doc.base_grand_total
		else:
			grand_total = doc.rounded_total or doc.grand_total
		outstanding_amount = doc.outstanding_amount
	elif dt == "Dunning":
		grand_total = doc.grand_total
		outstanding_amount = doc.grand_total
	else:
		if party_account_currency == doc.company_currency:
			grand_total = flt(doc.get("base_rounded_total") or doc.get("base_grand_total"))
		else:
			grand_total = flt(doc.get("rounded_total") or doc.get("grand_total"))
		outstanding_amount = doc.get("outstanding_amount")
	return grand_total, outstanding_amount

@frappe.whitelist()
def udpate_advance_payment_on_master(self):
	if frappe.db.exists("Advance Fees", {"registration_number": self.registration_number}):
		adv = frappe.get_doc("Advance Fees", {"registration_number": self.registration_number})

		for child in self.advance_payment:
			existing_child = next(
				(row for row in adv.advance_payment if row.reference_type == child.reference_type and row.reference_number == child.reference_number),
				None
			)

			if existing_child:
				existing_child.adjusted_amount += child.adjusted_amount
				existing_child.balance_amount = child.received_amount - existing_child.adjusted_amount

		adv.save()

  
@frappe.whitelist()
def validate_paying_amount(self):
	index = 0
	for row in self.components:
		index += 1
		if row.paying_amount:
			if row.paying_amount > row.outstanding_amount:
				frappe.throw(f"<b>Row {index}</b>: Paying Amount is greater than the Outstanding Amount")

@frappe.whitelist()
def validate_excess_amount(self):
	if self.pay_advance == 1 and self.excess_amount <= 0:
		frappe.throw("Value cannot be zero for Fees Collection: <strong>Excess Amount</strong>", 
					frappe.NonNegativeError, title=_("Zero Value")
					)

# Advance Fee on submission
@frappe.whitelist()
def update_advance_fees(self):
		if self.pay_advance and self.excess_amount > 0:
			advance_fees = frappe.db.exists("Advance Fees", {"registration_number": self.registration_number})
			if advance_fees:
				adv = frappe.get_doc("Advance Fees", {"registration_number": self.registration_number})
				adv.student = self.student
				adv.append('advance_payment', {
					"reference_type": "Fees Collection",
					"reference_number": self.name,
					"date": today(),
					"received_amount": self.excess_amount,
					"balance_amount": self.excess_amount
				})
				adv.save()
			else:
				adv = frappe.new_doc("Advance Fees")
				adv.registration_number = self.registration_number
				adv.student = self.student
				adv.append('advance_payment', {
					"reference_type": "Fees Collection",
					"reference_number": self.name,
					"date": today(),
					"received_amount": self.excess_amount,
					"balance_amount": self.excess_amount
				})
				adv.save()
				
@frappe.whitelist()
def create_concession(self):
	concession_exist = frappe.db.exists("Concession", 
										{"student": self.student, "academic_year": self.academic_year, 
										 "academic_term": self.academic_term, "program": self.program, "docstatus": 1
		   								})
	if concession_exist:
		if self.mark_concession and self.concession_amount > 0 and self.concession_on :
			frappe.throw("Concession has already been applied for this semester")
	if not concession_exist:								
		if self.mark_concession and self.concession_amount > 0 and self.concession_on :
			concession = frappe.new_doc("Concession")
			concession.student = self.student
			concession.academic_year = self.academic_year
			concession.academic_term = self.academic_term
			concession.program = self.program
			concession.concession_amount = self.concession_amount
			concession.fees = self.fees
			concession.fees_collection = self.name
			concession.concession_on = self.concession_on
			concession.save(ignore_permissions=True)
			concession.submit()
   
@frappe.whitelist()
def update_concession_on_paying_amount(self):
	if self.mark_concession and self.concession_amount > 0 and self.concession_on:
		index = 0
		for row in self.components:
			index += 1
			if row.fees_category == self.concession_on:
				if row.outstanding_amount >= self.concession_amount:
					if row.outstanding_amount >= self.concession_amount + row.paying_amount:
						row.amount -= self.concession_amount
						row.outstanding_amount -= self.concession_amount
					else:
						frappe.throw(f"<b>Row {index}:</b> Concession Amount + Paying Amount is greater than the Outstanding Amount")
				else:
					frappe.throw(f"<b>Row {index}:</b> Concession Amount is greater than the Outstanding Amount")	
	 
@frappe.whitelist()
def total_of_all_ammounts(self):
	amount = 0
	amount_paid = 0
	outstanding_amount = 0
	paying_amount = 0
	for row in self.components:
		amount += row.amount
		amount_paid += row.amount_paid
		outstanding_amount += row.outstanding_amount
		paying_amount += row.paying_amount
	self.grand_total = amount
	self.amount_paid = amount_paid
	self.outstanding_amount = outstanding_amount
	self.paying_amount = paying_amount

# Updating paid amount on Fees Master while submitting the Fees Collection 
@frappe.whitelist()
def update_paid_amount(self):
	fees = frappe.get_doc("Fees", self.fees)
	fees.set('components', [])
	outstanding=0
	for row in self.components:
		fees.append("components", {
					"fees_category": row.fees_category,
					"description": row.description,
					"amount": row.amount,
					"custom_amount_paid": row.amount_paid + row.paying_amount,
					"custom_outstanding_amount": row.amount - row.amount_paid - row.paying_amount
				
				})
	# 	outstanding+=(row.amount - row.amount_paid - row.paying_amount)
	# fees.outstanding_amount=outstanding
	fees.save(ignore_permissions=True)
	frappe.db.commit()
 
@frappe.whitelist()
def validate_amount_paid(self):
	tot = 0
	for row in self.components:
		tot += row.paying_amount
	if tot == 0:
		frappe.throw("Could not save document with <b>zero payment</b>")
	
# to update outstanding_amount in fee master
@frappe.whitelist()
def update_outstanding_amount(fee_name):
	fees = frappe.get_doc("Fees", fee_name)
	tot_out = 0
	tot_amt = 0
	for row in fees.components:
		tot_out += row.custom_outstanding_amount
		tot_amt += row.amount
	fees.outstanding_amount = tot_out
	fees.grand_total = tot_amt
	fees.grand_total_in_words = money_in_words(fees.grand_total)
	fees.save(ignore_permissions=True)
	frappe.db.commit()
 
@frappe.whitelist()
def cancel_fees_collection(self):
	if frappe.db.exists("Payment Entry", {"custom_reference_docname": self.name, "docstatus": 1}):
		pe = frappe.get_doc("Payment Entry", {"custom_reference_docname": self.name})
		pe.cancel()

	# Revert fees total amount 
	fees = frappe.get_doc("Fees", self.fees)
	for child in self.components:
		for row in fees.components:
			if child.fees_category == row.fees_category:
				# If there is a concession
				if self.mark_concession and self.concession_amount > 0 and self.concession_on:
					if row.fees_category == self.concession_on:
						row.amount += self.concession_amount
				row.custom_amount_paid = row.custom_amount_paid - child.paying_amount
				row.custom_outstanding_amount = row.amount - row.custom_amount_paid
					 
	fees.save(ignore_permissions=True)
	update_outstanding_amount(fees.name)
	
	if frappe.db.exists("Advance Fees", {"registration_number":self.registration_number}):
		adv = frappe.get_doc("Advance Fees", {"registration_number":self.registration_number})
		adj_amt = 0
		for row in self.advance_payment:
			for child in adv.advance_payment:
				if row.reference_type == child.reference_type and row.reference_number == child.reference_number:
					if row.adjusted_amount > 0:
						child.adjusted_amount = child.adjusted_amount - row.adjusted_amount
						child.balance_amount = child.balance_amount + row.adjusted_amount
						child.adjusted = 0
		adv.save(ignore_permissions=True)
		
	if frappe.db.exists("Concession", {"fees_collection": self.name, "docstatus": 1}):
		concession = frappe.get_doc("Concession", {"fees_collection": self.name})
		concession.cancel()
		
	   