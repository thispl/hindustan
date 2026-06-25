// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Registration", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('Update Student Name', () => {
                let d = new frappe.ui.Dialog({
                    title: 'Update Student Name',
                    fields: [{
                        label: 'New Student Name',
                        fieldname: 'updated_name',
                        fieldtype: 'Data',
                        reqd: true
                    }],
                    primary_action_label: 'Update',
                    primary_action(values) {
                        frappe.call({
                            method: "hindustan.hindustan.doctype.registration.registration.update_student_name_from_registration",
                            args: {
                                name: frm.doc.name,
                                updated_name: values.updated_name
                            },
                            callback: function(r) {
                                if (r.message === "Success") {
                                    frappe.msgprint('Student Name Updated Successfully!');
                                    frm.reload_doc();
                                }
                            }
                        });
                        d.hide();
                    }
                });
                d.show();
            });
        }
    },
    // after_insert: function(frm){
    //     console.log('message')
	// 	frappe.call({
    //         method: "hindustan.hindustan.doctype.registration.registration.get_rec_no",
    //         callback(r){
    //             if (r.message){
    //                 console.log('message')
    //                 console.log(r.message)
    //                 frm.set_value("receipt_number",r.message)
    //             }
    //             else{
    //                 frm.set_value("receipt_number",'')
    //             }
    //         }
    //     })
	// 	frm.save()
	// 	frm.reload_doc()
	// },
    institution_name(frm) {
        if (!frm.doc.is__islocal){
            if (frm.doc.institution_name){
                frappe.call({
                    method: "hindustan.hindustan.doctype.registration.registration.get_reg_no",
                    args: {
                        'ins' : frm.doc.institution_name,
                        'name' : frm.doc.name                  
                    },
                    callback(r){
                        if (r.message){
                            frm.set_value("registration_number",r.message)
                        }
                        else{
                            frm.set_value("registration_number",'')
                        }
                    }
                   
                })
            }
            else{
                frm.set_value("registration_number",'')
            }
            
        }
		frm.set_query('academic_term', function() {
			return {
				'filters':{
					'academic_year': frm.doc.academic_year,
                    'program':frm.doc.program
				}
			};
		});
    },
    onload(frm){
        if (!frm.doc.receipt_number){
                frappe.call({
                    method: "hindustan.hindustan.doctype.registration.registration.get_rec_no",
                    callback(r){
                        if (r.message){
                            frm.set_value("receipt_number",r.message)
                        }
                        else{
                            frm.set_value("receipt_number",'')
                        }
                    }
                })
            }
        if (!frm.doc.program){
            frm.set_df_property('academic_year','hidden',1);
            frm.set_df_property('academic_term','hidden',1);
        }
    },
    academic_year(frm) {
		frm.trigger('get_amount')
	},
	program(frm) {
        frm.set_df_property('academic_year','hidden',0);
        frm.set_df_property('academic_term','hidden',0);
		frm.trigger('get_amount')
	},
	student_category(frm) {
		frm.trigger('get_amount')
	},
    academic_term(frm) {
		frm.trigger('get_amount')
	},
	get_amount(frm) {
		if (frm.doc.academic_term && frm.doc.student_category && frm.doc.program && frm.doc.academic_year) {
            frappe.call({
                method: "hindustan.hindustan.doctype.registration.registration.get_reg_amount",
                args: {
                    sem : frm.doc.academic_term,
                    category:frm.doc.student_category,
                    year:frm.doc.academic_year,
                    program:frm.doc.program,
                },
                callback(r){
                    if (r.message){
                        frm.set_value("course_registration_fee",r.message)
                    }
                    else{
                        frm.set_value("course_registration_fee",'')
                    }
                }
            })
		}
        
	},
    setup(frm){
        frm.set_query('program', function() {
			return {
				'filters':{
					'custom_institute_name': frm.doc.institution_name,
				}
			};
		});
    }
});
