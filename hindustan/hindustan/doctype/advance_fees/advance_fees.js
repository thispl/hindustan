// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advance Fees", {
	onload: function(frm) {
		frm.set_query('academic_term', function() {
			return {
				'filters':{
					'academic_year': frm.doc.academic_year
				}
			};
		});
    },
    registration_number(frm) {
        if (frm.doc.registration_number) {
            frappe.db.get_value(
                "Student",
                { "custom_registration_number": frm.doc.registration_number },
                ['name', 'custom_academic_year', 'custom_current_academic_term', 'custom_program']
            ).then(r => {
                if (r && r.message) {
                    let student = r.message;
                    frm.set_value('student_name', student.name);
                    frm.set_value('academic_year', student.custom_academic_year);
                    frm.set_value('academic_term', student.custom_current_academic_term);
                    frm.set_value('program', student.custom_program);
                } else {
                    frappe.msgprint(__('No Student found with this Registration Number'));
                }
            })
        } else {
            frappe.msgprint(__('Please enter a Registration Number'));
        }
    }
    
});
