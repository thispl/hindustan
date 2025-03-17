// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.query_reports["Registration"] = {
	"filters": [
		{
			"label": __("From Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"label": __("To Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"label": __("Institution"),
			"fieldname": "institution",
			"fieldtype": "Link",
			"options": "Institute"
		},
		{
			"label": __("Program"),
			"fieldname": "program",
			"fieldtype": "Link",
			"options": "Program"
		},
		// {
		// 	"label": __("Course"),
		// 	"fieldname": "course",
		// 	"fieldtype": "Link",
		// 	"options": "Course"
		// },
		
		{
			"label": __("Student Category"),
			"fieldname": "student_category",
			"fieldtype": "Link",
			"options": "Student Category"
		},
		{
			"label": __("Registration Number"),
			"fieldname": "registration_number",
			"fieldtype": "Link",
			"options": "Registration"
		},
		{
			"label": __("Academic Year"),
			"fieldname": "academic_year",
			"fieldtype": "Link",
			"options": "Academic Year"
		},
		{
			"label": __("Concession Applicability"),
			"fieldname": "concession_applicability",
			"fieldtype": "Check",
			"options": " "
		},
		{
			"label": __("Payment Mode"),
			"fieldname": "payment_mode",
			"fieldtype": "Select",
			"options": " \nDD\nCheque\nCash\nMO\nOnline Transfer\nGPAY / sQR Code"
		},
		// {
		// 	"label": __("Due Payment"),
		// 	"fieldname": "due_payment",
		// 	"fieldtype": "Float",
		// 	// "precision": 2
		// }
		
	]

};
