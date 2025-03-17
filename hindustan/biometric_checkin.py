import frappe

@frappe.whitelist(allow_guest=True)
def mark_checkin(**args):
	if frappe.db.exists('Employee',{'attendance_device_id':args['employee']}):
		emp=frappe.db.get_value("Employee",{'attendance_device_id':args['employee']},['name'])
		if not frappe.db.exists('Employee Checkin',{'employee':emp,'time':str(args['time'])}):
			ec = frappe.new_doc('Employee Checkin')
			ec.employee = frappe.get_value('Employee',{'attendance_device_id':args['employee']},['name'])
			ec.device_code = args['employee'].upper()
			ec.time = args['time']
			ec.device_id = args['device_id']
			ec.save(ignore_permissions=True)
			frappe.db.commit()
			return "Checkin Marked"
		else:
			return "Checkin Marked"
	else:
		if not frappe.db.exists('Unregistered Employee Checkin',{'employee':str(args['employee']),'time':str(args['time'])}):
			uec = frappe.new_doc('Unregistered Employee Checkin')
			uec.employee = args['employee'].upper()
			# uec.time = args['time']
			uec.device_id = args['device_id']
			uec.save(ignore_permissions=True)
			frappe.db.commit()
			return "Checkin Marked"
		else:
			return "Checkin Marked"