// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Report Dashboard", {
	to_date(frm) {
        if(frm.doc.to_date<frm.doc.from_date){
            frm.set_value("to_date","")
            frappe.throw("Enter Valid TO Date")
        }
	},
    download(frm){
        if (frm.doc.report == 'Consolidated statement') {
            var path = "hindustan.hindustan.doctype.report_dashboard.consolidated_report.consolidated_salary_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                    "&institute_name=" + encodeURIComponent(frm.doc.institute_name)+
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.department);
        }
        else if (frm.doc.report == 'Salary Register') {
            var path = "hindustan.hindustan.doctype.report_dashboard.salary_register.salary_register_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                        "&institute_name=" + encodeURIComponent(frm.doc.institute_name) + 
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.department);
        }
        else if (frm.doc.report == 'Payment Report') {
            var path = "hindustan.hindustan.doctype.report_dashboard.payment_report.payment_report_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                        "&institute_name=" + encodeURIComponent(frm.doc.institute_name) + 
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.department);
        }
        else if (frm.doc.report == 'Consolidated Salary statement') {
            var path = "hindustan.hindustan.doctype.report_dashboard.consolidated_salary_statement.consolidated_salary_statement_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                        "&institute_name=" + encodeURIComponent(frm.doc.institute_name) + 
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.department);
        }
        else if (frm.doc.report == 'Transfer Statement') {
            var path = "hindustan.hindustan.doctype.report_dashboard.report_dashboard.transfer_statement_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                        "&institute_name=" + encodeURIComponent(frm.doc.institute_name) + 
                    "&to_date=" + encodeURIComponent(frm.doc.to_date)+ "&dept=" + encodeURIComponent(frm.doc.department);
        }
        if (path) {
            const url = `${frappe.request.url}?cmd=${encodeURIComponent(path)}&${args}`;
            window.location.href = url;
        }
    },
    pdf(frm){
        if (frm.doc.report == 'Consolidated Salary statement'){
            var print_format ="Consolidated Salary Statement";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
        }
    }
});
