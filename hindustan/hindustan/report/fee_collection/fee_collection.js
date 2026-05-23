// Copyright (c) 2025, Abdulla PI and contributors
// For license information, please see license.txt

frappe.query_reports["Fee Collection"] = {
	"filters": [
		{
			"label": __("Student"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student",
			// "reqd": 1,
		},
		{
			"label": __("Admission"),
			"fieldname": "admission",
			"fieldtype": "Link",
			"options": "Admission",
			// "reqd": 1,
			"get_query": function() {
				return {
					filters: {
						"docstatus": 1 
					}
				};
			}
		},
	]
};
