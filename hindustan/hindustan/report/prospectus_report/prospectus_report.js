// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.query_reports["Prospectus report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			'reqd':1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			'reqd':1
		},
	
		{
			"fieldname": "institution_name",
			"label": __(" Institute Name"),
			"fieldtype": "Link",
			"options": "Institute"
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"options": "\nDD\nCheque\nCash\nMO\nOnline Transfer\nGPAY / QR Code"			
	
			
		}

	]
};
