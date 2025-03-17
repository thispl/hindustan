// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Admission", {
    before_submit: function(frm) {
        if (!frm.doc.aadhar_number){
        return new Promise((resolve, reject) => {
            frappe.confirm(
                'Are you sure you want to submit this document without Aadhar Number?', 
                () => resolve(),  // If user clicks "Yes", allow submission
                () => reject()     // If user clicks "No", prevent submission
            );
        });
    }
    },
	institution_name(frm) {
        if (!frm.doc.is__islocal){
            if (frm.doc.institution_name){
                frappe.call({
                    method: "hindustan.hindustan.doctype.admission.admission.get_adm_no",
                    args: {
                        'ins' : frm.doc.institution_name,
                        'name' : frm.doc.name                  
                    },
                    callback(r){
                        if (r.message){
                            frm.set_value("admission_number",r.message)
                        }
                        else{
                            frm.set_value("admission_number",'')
                        }
                    }
                   
                })
            }
            else{
                frm.set_value("admission_number",'')
            }
        }
	},
	onload: function(frm) {
		frm.set_query('registration_number', function() {
			return {
				'filters':{
					'docstatus':1
				}
			};
		});
        frm.set_query('program', function() {
            return {
                'filters':{
                    'custom_institute_name': frm.doc.institution_name,
                }
            };
        });
        frm.set_query('batch__semester', function() {
			return {
				'filters':{
					'academic_year': frm.doc.academic_year,
                    'program':frm.doc.program
				}
			};
		});
        
    },
});
