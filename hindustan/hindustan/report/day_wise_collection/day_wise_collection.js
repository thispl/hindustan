// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.query_reports["Day Wise Collection"] = {
	onload: function (report) {
        frappe.breadcrumbs.add({
            module: "Education",
            label: "Day Wise Collection",
        });
    },
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
			"label": __("Program Wise"),
			"fieldname": "program_wise",
			"fieldtype": "Link",
			"options": "Program"
		},
		{
			"label": __("Student"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student"
		},
		{
			"label": __("Admission"),
			"fieldname": "admission",
			"fieldtype": "Link",
			"options": "Admission",
			"get_query": function() {
				return {
					filters: {
						"docstatus": 1 // Only show submitted Admission documents
					}
				};
			}
		},
		{
			"label": __("Academic Year"),
			"fieldname": "academic_wise",
			"fieldtype": "Link",
			"options": "Academic Year"
		},
		{
			"label": __("Academic Term"),
			"fieldname": "academic_term",
			"fieldtype": "Link",
			"options": "Academic Term"
		},
		{
			"label": __("Bill Wise"),
			"fieldname": "bill_wise",
			"fieldtype": "Select",
			"options": " \nAdmission\nFees Collection\nProspectus\nRegistration\nGeneral Receipt"
		},
		// {
		// 	"label": __("Fee"),
		// 	"fieldname": "fee",
		// 	"fieldtype": "Link",
		// 	"options": "Fee Category",
		// 	"depends_on": "eval:doc.bill_wise == 'Fee'"
		// }
	]
};
