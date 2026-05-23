// Copyright (c) 2025, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("General Receipt", {
	onload(frm) {
        if (!frm.doc.reciept_number){
            frappe.call({
                method: "hindustan.hindustan.doctype.general_receipt.general_receipt.get_rec_no",
                callback(r){
                    if (r.message){
                        frm.set_value("reciept_number",r.message)
                    }
                    else{
                        frm.set_value("reciept_number",'')
                    }
                }
            })
        }
        frm.set_query('recieved_person', function() {
            return {
                filters: {
                    is_student: frm.doc.is_student ? 1 : 0
                }
            };
        });
        if(frm.doc.is_student==1){
		    frm.set_df_property('received_amount', 'label', 'Refund Amount');
            frm.refresh_field('received_amount');
		}else{
		    frm.set_df_property('received_amount', 'label', 'Received Amount');
            frm.refresh_field('received_amount');
		}
	},
    
    is_student(frm) {
        frm.set_query('recieved_person', function() {
            return {
                filters: {
                    is_student: frm.doc.is_student ? 1 : 0
                }
            };
        });
        if(frm.doc.is_student==1){
		    frm.set_df_property('received_amount', 'label', 'Refund Amount');
            frm.refresh_field('received_amount');
		}else{
		    frm.set_df_property('received_amount', 'label', 'Received Amount');
            frm.refresh_field('received_amount');
		}
    },
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

});
