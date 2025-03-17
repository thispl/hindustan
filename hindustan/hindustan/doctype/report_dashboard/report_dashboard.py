# # Copyright (c) 2024, Abdulla PI and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReportDashboard(Document):
    pass

import frappe
from io import BytesIO
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment, Border, Side,Font

@frappe.whitelist()
def transfer_statement_download():
    filename = "TRANSFER STATEMENT"
    build_xlsx_response_ts(filename)

def build_xlsx_response_ts(filename):
    xlsx_file = make_xlsx_css(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'

def make_xlsx_css(sheet_name="TRANSFER STATEMENT", wb=None):
    if wb is None:
        wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = sheet_name
    args = frappe.local.form_dict
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    from_date_str = args.get('from_date')
    to_date_str = args.get('to_date')
    institute=args.get('institute_name')
    if not from_date_str or not to_date_str:
        frappe.throw("Both 'From date' and 'To date' must be provided.")

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

    # Define column widths
    column_widths = {
        'A': 7, 'B': 18, 'C': 25, 'D': 25,'E':25,'F':25,'G':25
    
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Adding header rows
    if institute:
        ws.append([f"{institute}"])
    else:
        ws.append(["HINDUSTAN ACADEMY"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=7)
    ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')

    ws.append(["BANGALORE"])
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

    month_year = from_date.strftime('%B %Y')
    month_year=str(month_year).upper()
    ws.append([f"TRANSFER STATEMENT FOR THE MONTH - {month_year}"])
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=7)
    ws.cell(row=3, column=1).alignment = Alignment(horizontal='center', vertical='center')
    sub_header = [
        "SI NO", "Employee","Employee Name" ,"Bank Name", "Account Number", "IFSC Code","Net Pay"
    ]
    ws.append(sub_header)
    bold_font = Font(bold=True)
    for cell in ws[4]:
        cell.font = bold_font
    data = get_data_for_ts(args)
    for row in data:
        ws.append(row)
    frappe.errprint(data)
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=7):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')

    # Save the workbook to a BytesIO object
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)

    return xlsx_file

def get_data_for_ts(args):
    s_no = 0
    data = []
    filters = {"start_date": args.from_date, "docstatus": ['!=', 2]}
    if args.dept and args.institute:   
        salary_slips = frappe.db.get_all("Salary Slip", {"start_date": args.from_date,'custom_institute_name':args.institute,'department':args.dept,'docstatus':['!=',2]}, ['employee', 'employee_name', 'net_pay'])
    elif args.dept and not args.institute:   
        salary_slips = frappe.db.get_all("Salary Slip", {"start_date": args.from_date,'department':args.dept,'docstatus':['!=',2]}, ['employee', 'employee_name', 'net_pay'])
    elif not args.dept and args.institute:   
        salary_slips = frappe.db.get_all("Salary Slip", {"start_date": args.from_date,'custom_institute_name':args.institute,'docstatus':['!=',2]}, ['employee', 'employee_name', 'net_pay'])
    else:   
        salary_slips = frappe.db.get_all("Salary Slip", {"start_date": args.from_date,'docstatus':['!=',2]}, ['employee', 'employee_name', 'net_pay'])
    employees = frappe.db.get_all("Employee", 
                                  {"name": ["in", [slip['employee'] for slip in salary_slips]]},
                                  ["name", "bank_ac_no", "ifsc_code", "bank_name"])
    
    employee_data = {emp['name']: emp for emp in employees}
    for slip in salary_slips:
        s_no += 1
        emp_details = employee_data.get(slip['employee'], {})
        bank_name = emp_details.get("bank_name", '')
        bank_account = emp_details.get("bank_ac_no", '')
        ifsc_code = emp_details.get("ifsc_code", '')
        row = [s_no, slip['employee'], slip['employee_name'], bank_name or '-', bank_account or '-', ifsc_code or '-', slip['net_pay']]
        data.append(row)
    
    return data
 

    