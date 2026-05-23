# Copyright (c) 2025, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe import _
def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_columns():
	return [
		_("Student ID") + ":Link/Student:150",
		_("Student Name") + ":Data:200",
		_("Admission") + ":Link/Admission:150",
		_("Program") + ":Data:150",
		_("Semester") + ":Data:150",
		_("Fee Category") + ":Data:150",
		_("Receipt No") + ":Data:150",
		_("Payment Date") + ":Data:120",
		_("Amount") + ":Currency:120",
	]

def get_data(filters):
	condition = add_filters(filters)
	sql, params = get_fee_data(condition)    
	registration_data = frappe.db.sql(sql, params, as_dict=True)
	data = []
	added_registration_students = set()  
	for row in registration_data:
		paid_amount = frappe.get_doc("Fees Collection", row.name)
		sem=frappe.db.get_value('Academic Term',{'name': paid_amount.academic_term},['custom_semester'])
		if not sem:
			sem=0
		for i in paid_amount.components:
			if row.payment_date:
				due_date_str =row.payment_date.strftime('%Y-%m-%d')
				due_date_str = datetime.strptime(due_date_str, "%Y-%m-%d") 
				formatted_pay_date = due_date_str.strftime("%d-%m-%Y")
			else:
				formatted_pay_date='' 
			if i.paying_amount > 0:
				data.append([
					row.student, row.student_name, row.admission, row.program,sem,
					i.fees_category, row.receipt_number, formatted_pay_date, i.paying_amount
				])
		
		if row.student not in added_registration_students:
			reg = frappe.db.get_value("Student", {'name': row.student}, ['custom_registration_number'])
			if reg and frappe.db.exists("Registration", {'name': reg, 'docstatus': 1}):
				reg_doc = frappe.get_doc("Registration", {'name': reg, 'docstatus': 1})
				sem1=frappe.db.get_value('Academic Term',{'name': reg_doc.academic_term},['custom_semester'])
				if not sem1:
					sem1=0
				if reg_doc.amount_paid > 0:
					payment_date = reg_doc.payment_date or reg_doc.date
					if payment_date:
						due_date_str =payment_date.strftime('%Y-%m-%d')
						due_date_str = datetime.strptime(due_date_str, "%Y-%m-%d") 
						formatted_due_date = due_date_str.strftime("%d-%m-%Y")
					else:
						formatted_due_date='' 
					data.append([
						row.student, row.student_name, row.admission, row.program,sem1,
						'Registration Fee', reg_doc.receipt_number, formatted_due_date, reg_doc.amount_paid
					])
					added_registration_students.add(row.student)  

	return data



def add_filters(filters):
	condition = {
		"docstatus": 1,
	}
	if filters.get("student"):
		condition["student"] = filters.get("student")
	if filters.get("admission"):
		condition["admission"] = filters.get("admission")
	return condition

def get_fee_data(condition):
	sql = """
		SELECT 
		name,receipt_number, payment_date, student,student_name,admission,program,academic_term 
	FROM `tabFees Collection`
	WHERE docstatus = 1
	""" 
	params = []
	if "student" in condition:
		sql += " AND student = %s"
		params.append(condition["student"])
	if "admission" in condition:
		sql += " AND admission = %s"
		params.append(condition["admission"])
	sql += " ORDER BY admission ASC"
	return sql, params
