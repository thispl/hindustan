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
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.custom_section);
        }
        else if (frm.doc.report == 'Salary Register') {
            var path = "hindustan.hindustan.doctype.report_dashboard.salary_register.salary_register_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                        "&institute_name=" + encodeURIComponent(frm.doc.institute_name) + 
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.custom_section);
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
                    "&to_date=" + encodeURIComponent(frm.doc.to_date) + "&dept=" + encodeURIComponent(frm.doc.custom_section);
        }
        else if (frm.doc.report == 'Transfer Statement') {
            var path = "hindustan.hindustan.doctype.report_dashboard.report_dashboard.transfer_statement_download";
            var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
                        "&institute_name=" + encodeURIComponent(frm.doc.institute_name) + 
                    "&to_date=" + encodeURIComponent(frm.doc.to_date)+ "&dept=" + encodeURIComponent(frm.doc.custom_section);
        }
        if (path) {
            const url = `${frappe.request.url}?cmd=${encodeURIComponent(path)}&${args}`;
            window.location.href = url;
        }
    },
    pdf(frm) {
        trigger_pdf_download(frm);
    },
    salary_register_pdf(frm) {
        trigger_pdf_download(frm);
    },
    consolidated_statement_pdf(frm) {
        trigger_pdf_download(frm);
    }
});

function trigger_pdf_download(frm) {
    if (!frm.doc.from_date || !frm.doc.to_date) {
        frappe.throw(__("Please select From Date and To Date"));
        return;
    }

    frm.save().then(() => {
        if (frm.doc.report === "Transfer Statement") {
            let path = "hindustan.hindustan.doctype.report_dashboard.report_dashboard.transfer_statement_pdf_download";
            let args = {
                from_date: frm.doc.from_date || "",
                to_date: frm.doc.to_date || "",
                institute_name: frm.doc.institute_name || "",
                dept: frm.doc.custom_section || ""
            };
            let query = Object.keys(args)
                .map(key => key + "=" + encodeURIComponent(args[key]))
                .join("&");

            window.open("/api/method/" + path + "?" + query);
            return;
        }

        let print_format = "";
        if (frm.doc.report === "Salary Register") {
            print_format = "Salary Register";
        } else if (frm.doc.report === "Consolidated Salary statement" || frm.doc.report === "Consolidated statement") {
            print_format = "Consolidated Salary Statement";
        }

        if (print_format) {
            window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                + "doctype=" + encodeURIComponent("Report Dashboard")
                + "&name=" + encodeURIComponent(frm.doc.name)
                + "&trigger_print=1"
                + "&format=" + encodeURIComponent(print_format)
                + "&no_letterhead=0"
            ));
        }
    });
}
