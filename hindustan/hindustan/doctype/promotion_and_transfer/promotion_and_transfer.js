// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Promotion And Transfer", {
    onload: function(frm) {
		frm.set_query('promotion_sem__batch', function() {
			return {
				'filters':{
					'academic_year': frm.doc.promotion_academic_year
				}
			};
		});
    },
    before_save(frm){
        if(frm.doc.promotion__transfer==1){
            frm.set_value('naming_series',"PRO.#####")
        }
        else if(frm.doc.transfer==1){
            frm.set_value('naming_series',"TRA.#####")
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

	get_students(frm){
        if(!frm.doc.institute_name){
            frappe.throw("Kindly fill the Institute name")
        }
        if(!frm.doc.program){
            frappe.throw("Kindly fill the Program")
        }
        if(!frm.doc.academic_year){
            frappe.throw("Kindly fill the Academic Year")
        }
        if(!frm.doc.batchsem){
            frappe.throw("Kindly fill the Batch/Sem")
        }
        if(frm.doc.student_id__admission_id){
            frm.set_value("student_id__admission_id","")
            frappe.throw("Not allow to Promote or Transfer Single Student and Multiple Student at same time")
            
        }
        else if(!frm.doc.student_id__admission_id){
            frappe.call({
                method:"hindustan.hindustan.doctype.promotion_and_transfer.promotion_and_transfer.get_student_details",
                args:{
                    inst_name:frm.doc.institute_name,
                    program:frm.doc.program,
                    year:frm.doc.academic_year,
                    sem:frm.doc.batchsem
                },
                callback(r){
                    if(r.message){
                        frm.clear_table("student_promotion");
                        $.each(r.message, function (i, student) {
                            let child = frm.add_child("student_promotion");
                            child.student_id__admission_id = student[0];
                            child.program = student[1];
                            child.batchsem = student[2]; 
                            // child.section = student[3]; 
                        });
                        frm.save()
                        frm.refresh_field("student_promotion");
                    }
                    
                }
            })
        }
    },
    get_student(frm){
        if(!frm.doc.institute_name){
            frappe.throw("Kindly fill the Institute name")
        }
        if(!frm.doc.program){
            frappe.throw("Kindly fill the Program")
        }
        if(!frm.doc.academic_year){
            frappe.throw("Kindly fill the Academic Year")
        }
        if(!frm.doc.batchsem){
            frappe.throw("Kindly fill the Batch/Sem")
        }
        if(frm.doc.promotion_via_assessment==1){
            frappe.call({
                method:"hindustan.hindustan.doctype.promotion_and_transfer.promotion_and_transfer.get_student_detail_assessment",
                args:{
                    program:frm.doc.program,
                    academic_year:frm.doc.academic_year,
                    academic_term:frm.doc.batchsem,
                    institute_name:frm.doc.institute_name
                },
                callback(r){
                    if(r.message){
                        frm.clear_table("student_promotion");
                        $.each(r.message, function (i, student) {
                            let child = frm.add_child("student_promotion");
                            child.student_id__admission_id = student[0];
                            child.program = student[1];
                            child.batchsem = student[2]; 
                            // child.section = student[3]; 
                        });
                        frm.save()
                        frm.refresh_field("student_promotion");
                    }
                
                }
            })
        }
    },
    
});
