// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Prospectus", {
	onload(frm) {
        if (!frm.doc.is__islocal){
            console.log("Test")
            if (!frm.doc.receipt_number){
                frappe.call({
                    method: "hindustan.hindustan.doctype.prospectus.prospectus.get_rec_no",
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
        }
		
    },
    setup(frm){
        frm.set_query('program', function() {
			return {
				'filters':{
					'custom_institute_name': frm.doc.institution_name
				}
			};
		});
    }
});
