// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Concession", {
	before_cancel: function(frm) {
        if(!frm.doc.cancellation_remarks){
            frappe.validated = false;
            let d = new frappe.ui.Dialog({
                title: 'Provide Cancellation Remarks',
                fields: [
                    {
                        label: 'Cancellation Remarks',
                        fieldname: 'cancellation_remarks',
                        fieldtype: 'Small Text',
                        reqd: 1, 
                        allow_on_submit:1,
                    }
                ],
                primary_action_label: 'Cancel',
                primary_action(values) {
                    frm.set_value('cancellation_remarks', values.cancellation_remarks);
                    frm.save('Update')
                        .then(() => {
                            frappe.call({
                                method: 'frappe.client.cancel',
                                args: {
                                    doctype: frm.doc.doctype,
                                    name: frm.doc.name,
                                },
                                callback: function(r) {
                                    if (!r.exc) {
                                        frm.reload_doc();
                                    } 
                                },
                            });
                        })
        
                    d.hide();
                },
            });
        
            d.show();
            frm.reload_doc();
        }
    },

    onload: function(frm) {
		frm.set_query('academic_term', function() {
			return {
				'filters':{
					'academic_year': frm.doc.academic_year
				}
			};
		});
    },
});
