import frappe
from frappe.model.document import Document

import frappe
from io import BytesIO
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment, Border, Side,Font


@frappe.whitelist()
def salary_register_download():
    filename = "SALARY Register"
    build_xlsx_response_sr(filename)

def build_xlsx_response_sr(filename):
    xlsx_file = make_xlsx_for_sr(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'

def make_xlsx_for_sr(sheet_name="SALARY REGISTER", wb=None):
    if wb is None:
        wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = sheet_name
    args = frappe.local.form_dict

    from_date_str = args.get('from_date')
    to_date_str = args.get('to_date')

    if not from_date_str or not to_date_str:
        frappe.throw("Both 'from_date' and 'to_date' must be provided.")

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

    # Define column widths
    column_widths = {
        'A': 20, 'B': 20, 'C': 20, 'D': 20, 'E': 20, 'F': 20,
        'G': 20, 'H': 20, 'I': 20, 'J': 20, 'K': 25,'L':20,'M':20,'N':20,'O':20,'P':20,'Q':20
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    month_year = from_date.strftime('%B %Y')
    month_year=str(month_year).upper()
    ws.append([f"SALARY REGISTER FOR THE MONTH OF - {month_year}"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=17)
    ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
    sub_header = [
        "Name", "No:of Days", "Basic", "DA", "HRA", "Med",
        "Conv", "Allow", "Gross Salary", "Pay Loss", "PF","P Tax","Loan","Adv","Other Deductions","Total Ded","Nett Sal"
    ]
    ws.append(sub_header)
    bold_font = Font(bold=True)
    for cell in ws[2]:  # Header row is the second row
        cell.font = bold_font
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=17):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center') 

    data=get_data_for_sr(args)
    totals = [0] * 16
    for employee_name, employee_data in data.items():
        lop=employee_data.get("lop_amount", "0")-employee_data.get("gross_pay", "0")
        if lop<0:
            lop=0
        row = [
            employee_name,
            employee_data.get("no_of_days", "0"),
            employee_data.get("basic_amount", "0"),
            employee_data.get("da_amount", "0"),
            employee_data.get("hra_amount", "0"),
            employee_data.get("med_amount", "0"),
            employee_data.get("convey_amount", "0"),
            employee_data.get("allow_amount", "0"),
            employee_data.get("gross_pay", "0"),
            lop,
            employee_data.get("pf_amount", "0"),
            employee_data.get("ptax_amount", "0"),
            employee_data.get("loan_amount", "0"),
            employee_data.get("adv_amount", "0"),
            employee_data.get("other_deductions", "0"),
            employee_data.get("total_deductions", "0"),
            employee_data.get("net_pay", "0")
        ]
        ws.append(row)
        for i in range(1, 17):  
            totals[i-1] += float(row[i]) if row[i] else 0
    totals_row = ["Total"] + [str(int(total)) for total in totals]  
    ws.append(totals_row)
    ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=2)
    total_cell = ws.cell(row=ws.max_row, column=1)  # This is the merged cell (SI NO)
    total_cell.alignment = Alignment(horizontal='center', vertical='center')
    for cell in ws[ws.max_row]:  # Total row
        cell.font = bold_font
        
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=17):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    return xlsx_file


def get_data_for_sr(args):
    data = {}

    from_date = args.get("from_date")
    to_date = args.get("to_date")
    institute = args.get("institute_name")
    dept = args.get("dept")

    if not from_date or not to_date:
        frappe.throw("Both 'from_date' and 'to_date' are required.")

    institute_condition = ""
    if institute and not dept:
        institute_condition = "AND e.custom_institute_name = %s"
        params = (from_date, to_date, institute)
    elif not institute and dept:
        institute_condition = "AND e.department = %s"
        params = (from_date, to_date, dept)
    elif institute and dept:
        institute_condition = "AND e.custom_institute_name = %s AND e.department = %s"
        params = (from_date, to_date, institute, dept)
    else:
        institute_condition = ""
        params = (from_date, to_date)
    queries = {
        "no_of_days": """
            SELECT e.name AS employee_name, s.payment_days AS payment_days,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "basic_amount": """
            SELECT e.name AS employee_name, cs.amount AS basic_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            WHERE cs.salary_component = 'Basic' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "da_amount": """
            SELECT e.name AS employee_name, cs.amount AS da_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            WHERE cs.salary_component = 'Dearness Allowance' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "hra_amount": """
            SELECT e.name AS employee_name, cs.amount AS hra_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            WHERE cs.salary_component = 'House Rent Allowance' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "med_amount": """
            SELECT e.name AS employee_name, cs.amount AS med_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            WHERE cs.salary_component = 'Medical Allowance' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "convey_amount": """
            SELECT e.name AS employee_name, cs.amount AS convey_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            WHERE cs.salary_component = 'Conveyance' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "allow_amount": """
            SELECT e.name AS employee_name, cs.amount AS allow_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            WHERE cs.salary_component = 'Allowance' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "gross_pay": """
            SELECT e.name AS employee_name, s.gross_pay AS gross_pay,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "lop_amount": """
            SELECT e.name AS employee_name, e.custom_total_gross AS lop_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "pf_amount": """
            SELECT e.name AS employee_name, cs.amount AS pf_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE cs.salary_component = 'Provident Fund' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "ptax_amount": """
            SELECT e.name AS employee_name, cs.amount AS ptax_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE cs.salary_component = 'Professional Tax' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "loan_amount": """
            SELECT e.name AS employee_name, cs.amount AS loan_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE cs.salary_component = 'Loan' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "adv_amount": """
            SELECT e.name AS employee_name, cs.amount AS adv_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE cs.salary_component = 'Employee Advance' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "other_deductions": """
            SELECT e.name AS employee_name, cs.amount AS other_deductions,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE cs.salary_component = 'Others' AND s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "total_deductions": """
            SELECT e.name AS employee_name, s.total_deduction AS total_deductions,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE s.start_date BETWEEN %s AND %s {institute_condition}
        """,
        "net_pay": """
            SELECT e.name AS employee_name, s.net_pay AS net_pay,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            WHERE s.start_date BETWEEN %s AND %s {institute_condition}
        """
    }

    # Execute queries for each salary component and store the results in `data`
    for key, query in queries.items():
        result = frappe.db.sql(query.format(institute_condition=institute_condition), 
                               params, 
                               as_dict=True)
        
        for row in result:
            employee_name = row["emp"]
            if employee_name not in data:
                data[employee_name] = {}

            # Ensure payment_days is captured as an integer if it's present in the result
            if key == "no_of_days" and row.get("payment_days"):
                data[employee_name][key] = int(row["payment_days"])  # Ensure it's an integer
            else:
                data[employee_name][key] = row.get(key, "")  # For

    return data
