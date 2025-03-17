// // Copyright (c) 2024, Abdulla PI and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Overall Fee Structure", {
    refresh(frm) {
        frappe.breadcrumbs.add('Education', 'Overall Fee Structure');
    },
    onload(frm) {
        frm.trigger("get_fee_structure_html")
    },
    get_fee_structure_html: function (frm){
            frappe.call({
                method :'hindustan.hindustan.doctype.overall_fee_structure.overall_fee_structure.get_fees_structure_html',
                args:{
                    program : frm.doc.program,
                    name : frm.doc.name,
                    no_of_semesters :frm.doc.no_of_semesters,
                },
                callback: function (response) {
                    frm.fields_dict.fee_structure_html.$wrapper.empty().append(response.message);
                }
            });
        
    },
});

frappe.listview_settings['Overall Fee Structure'] = {
    onload: function (listview) {
        frappe.breadcrumbs.clear();
        frappe.breadcrumbs.add('Education', 'Overall Fee Structure');
    }
};
