import frappe
from frappe.model.document import Document

import frappe
from io import BytesIO
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment, Border, Side,Font

@frappe.whitelist()
def consolidated_salary_download():
    filename = "CONSOLIDATED SALARY STATEMENT"
    build_xlsx_response(filename)

def build_xlsx_response(filename):
    xlsx_file = make_xlsx(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'

def make_xlsx(sheet_name="CONSOLIDATED SALARY STATEMENT", wb=None):
    if wb is None:
        wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = sheet_name
    args = frappe.local.form_dict

    from_date_str = args.get('from_date')
    to_date_str = args.get('to_date')
    institute=args.get('institute_name')
    if not from_date_str or not to_date_str:
        frappe.throw("Both 'from_date' and 'to_date' must be provided.")

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

    # Define column widths
    column_widths = {
        'A': 5, 'B': 20, 'C': 20, 'D': 20, 'E': 20, 'F': 20,
        'G': 20, 'H': 20, 'I': 20, 'J': 20, 'K': 25
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Adding header rows
    if institute:
        ws.append([f"{institute}"])
    else:
        ws.append(["HINDUSTAN ACADEMY"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=11)
    ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
    ws.append(["BANGALORE"])
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=11)
    ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

    month_year = from_date.strftime('%B %Y')
    month_year=(str(month_year)).upper()
    ws.append([f"CONSOLIDATED SALARY STATEMENT FOR THE MONTH - {month_year}"])
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=11)
    ws.cell(row=3, column=1).alignment = Alignment(horizontal='center', vertical='center')

    # Adding sub-header
    sub_header = [
        "SI NO", "Section", "Gross Salary", "Loss Of Pay", "Provident Fund", "Prof. Tax",
        "Loan", "Salary Advance", "Other Deductions", "Total Deduction", "Net Payable Salary"
    ]
    ws.append(sub_header)
    bold_font = Font(bold=True)
    for cell in ws[4]:  # Header row is the second row
        cell.font = bold_font
    # Define border style
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    data = get_data(args)
    s_no = 1
    totals = [0] * 9  
    for row in data:
        lop=0
        if row.get("tot_gross", 0)-row.get("total_basic_amount", 0)<0:
            lop=0
        else:
            lop=row.get("tot_gross", 0)-row.get("total_basic_amount", 0)
        row_data = [
            s_no,
            row.get("department", "-"),
            row.get("total_basic_amount", 0),
            lop,
            row.get("total_pf_amount", 0),
            row.get("total_ptax_amount", 0),
            row.get("total_loan_amount", 0),
            "0",
            row.get("total_other_deductions", 0),
            row.get("total_deductions", 0),
            row.get("net_pay", 0)
        ]
        ws.append(row_data)
        tot=row.get("tot_gross", 0)-row.get("total_basic_amount", 0)
        if tot<0:
            tot=0
        totals[0] += row.get("total_basic_amount", 0) or 0
        totals[1] += tot
        totals[2] += row.get("total_pf_amount", 0) or 0
        totals[3] += row.get("total_ptax_amount", 0) or 0
        totals[4] += row.get("total_loan_amount", 0) or 0
        totals[5] += row.get("total_other_deductions", 0) or 0
        totals[6] += row.get("total_deductions", 0) or 0
        totals[7] += row.get("net_pay", 0) or 0
        s_no += 1
    totals_row = [
        "TOTAL", "-",totals[0],totals[1],totals[2],totals[3],totals[4],'0',totals[5],totals[6],totals[7]
    ]
    ws.append(totals_row)
    ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=2)
    total_cell = ws.cell(row=ws.max_row, column=1)  # This is the merged cell (SI NO)
    total_cell.alignment = Alignment(horizontal='center', vertical='center')
    for cell in ws[ws.max_row]:  # Total row
        cell.font = bold_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=11):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')

    # Save the workbook to a BytesIO object
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    return xlsx_file


def get_data(args):
    from_date = args.get("from_date")
    to_date = args.get("to_date")
    institute = args.get("institute_name")  # Add institute filter
    dept= args.get("dept")

    if not from_date or not to_date:
        frappe.throw("Both 'from_date' and 'to_date' are required.")

    # Build the WHERE condition for institute filter
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

    # Fetch basic salary data
    basic_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(s.gross_pay) AS total_basic_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)
    pf_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_pf_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            cs.salary_component = 'Provident Fund' 
            AND s.start_date = %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    # Fetch PTAX data
    ptax_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_ptax_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            cs.salary_component = 'Professional Tax' 
            AND s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    # Fetch Loan data
    loan = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_loan_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            cs.salary_component = 'Loan' 
            AND s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    # Fetch Other Deductions data
    other_deductions = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_other_deductions
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            cs.salary_component = 'Others' 
            AND s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    # Fetch Total Deductions data
    tot_deductions = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(s.total_deduction) AS total_deductions
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    # Fetch Net Payable Salary data
    net_payable_salary = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(s.net_pay) AS net_pay
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    data = {}
    for item in basic_data:
        department = item['department']
        data[department] = {
            "department": department,
            "total_basic_amount": item['total_basic_amount']
        }
    lop_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(e.custom_total_gross) AS tot_gross
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.start_date BETWEEN %s AND %s
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    for item in lop_data:
        department = item['department']
        if department in data:
            data[department]['tot_gross'] = item['tot_gross']
        else:
            data[department] = {
                "department": department,
                "tot_gross": item['tot_gross']
            }

    for item in pf_data:
        department = item['department']
        if department in data:
            data[department]['total_pf_amount'] = item['total_pf_amount']
        else:
            data[department] = {
                "department": department,
                "total_pf_amount": item['total_pf_amount']
            }

    for item in ptax_data:
        department = item['department']
        if department in data:
            data[department]['total_ptax_amount'] = item['total_ptax_amount']
        else:
            data[department] = {
                "department": department,
                "total_ptax_amount": item['total_ptax_amount']
            }

    for item in loan:
        department = item['department']
        if department in data:
            data[department]['total_loan_amount'] = item['total_loan_amount']
        else:
            data[department] = {
                "department": department,
                "total_loan_amount": item['total_loan_amount']
            }

    for item in other_deductions:
        department = item['department']
        if department in data:
            data[department]['total_other_deductions'] = item['total_other_deductions']
        else:
            data[department] = {
                "department": department,
                "total_other_deductions": item['total_other_deductions']
            }

    for item in tot_deductions:
        department = item['department']
        if department in data:
            data[department]['total_deductions'] = item['total_deductions']
        else:
            data[department] = {
                "department": department,
                "total_deductions": item['total_deductions']
            }

    for item in net_payable_salary:
        department = item['department']
        if department in data:
            data[department]['net_pay'] = item['net_pay']
        else:
            data[department] = {
                "department": department,
                "net_pay": item['net_pay']
            }

    return list(data.values())

