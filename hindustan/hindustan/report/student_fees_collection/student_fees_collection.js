// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.query_reports["Student Fees Collection"] = {
	"filters": [
		{
			"label": __("Student"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student",
		},
		{
			"label": __("Student Name"),
			"fieldname": "student_name",
			"fieldtype": "Data",
		},
		{
			"label": __("Institute"),
			"fieldname": "custom_institute",
			"fieldtype": "Link",
			"options": "Institute",
		},
		{
			"label": __("Academic Year"),
			"fieldname": "academic_year",
			"fieldtype": "Link",
			"options": "Academic Year",
		},
		{
			"label": __("Academic Term"),
			"fieldname": "academic_term",
			"fieldtype": "Link",
			"options": "Academic Term",
		},
		{
			"label": __("Program"),
			"fieldname": "program",
			"fieldtype": "Link",
			"options": "Program",
		},
	]
};
