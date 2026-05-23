import frappe
from frappe.model.document import Document
from decimal import Decimal
import frappe
from io import BytesIO
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment, Border, Side,Font
import math

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
        'A': 5, 'B': 20, 'C': 20, 'D': 20, 'E': 20, 'F': 20, 'G': 20, 'H': 20,
        'I': 20, 'J': 20, 'K': 20, 'L': 20, 'M': 25
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Adding header rows
    if institute:
        ws.append([f"{institute}"])
    else:
        ws.append(["EVEHANS ACADEMY"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=13)
    ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
    ws.append(["BANGALORE"])
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=13)
    ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

    month_year = from_date.strftime('%B %Y')
    month_year=(str(month_year)).upper()
    ws.append([f"CONSOLIDATED SALARY STATEMENT FOR THE MONTH - {month_year}"])
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=13)
    ws.cell(row=3, column=1).alignment = Alignment(horizontal='center', vertical='center')

    # Adding sub-header
    sub_header = [
        "SI NO", "Section", "Gross Salary", "Loss Of Pay", "Provident Fund", "Prof. Tax", "ESI", "TDS",
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
    totals = [0] * 11  
    for row in data:
        lop=0
        gross_round = int(row.get("total_basic_amount", 0) + 0.5)
        tot_gross_round = int(row.get("tot_gross", 0) + 0.5)
        
        lop = row.get("lop_amount", 0) or 0
        total_basic = Decimal(str(row.get("total_basic_amount", 0) or 0))
        total_deductions = Decimal(str(row.get("total_deductions", 0) or 0))
        lop_amount = Decimal(str(lop or 0))
        net_pay = total_basic - (total_deductions + lop_amount)

        row_data = [
            s_no,
            row.get("department", "-"),
            row.get("total_basic_amount", 0),
            lop,
            row.get("total_pf_amount", 0),
            row.get("total_ptax_amount", 0),
            row.get("total_esi_amount", 0),
            row.get("total_tds_amount", 0),
            row.get("total_loan_amount", 0),
            row.get("total_advance_amount", 0),
            row.get("total_other_deductions", 0),
            row.get("total_deductions", 0) + lop ,
            net_pay
        ]
        ws.append(row_data)
        tot=gross_round - tot_gross_round
        if tot<0:
            tot=0
        totals[0] += row.get("total_basic_amount", 0) or 0
        # totals[1] += round(tot)
        totals[1] += lop
        totals[2] += row.get("total_pf_amount", 0) or 0
        totals[3] += row.get("total_ptax_amount", 0) or 0
        totals[4] += row.get("total_esi_amount", 0) or 0
        totals[5] += row.get("total_tds_amount", 0) or 0
        totals[6] += row.get("total_loan_amount", 0) or 0
        totals[7] += row.get("total_advance_amount", 0) or 0
        totals[8] += row.get("total_other_deductions", 0) or 0
        # totals[9] += (row.get("total_deductions", 0) or 0) + round(tot)
        totals[9] += (row.get("total_deductions", 0) or 0) + lop
        totals[10] += net_pay
        s_no += 1
    totals_row = [
        "TOTAL", "-",totals[0],totals[1],totals[2],totals[3],totals[4],totals[5],totals[6],totals[7],totals[8],totals[9],totals[10]
    ]
    ws.append(totals_row)
    ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=2)
    total_cell = ws.cell(row=ws.max_row, column=1)  # This is the merged cell (SI NO)
    total_cell.alignment = Alignment(horizontal='center', vertical='center')
    for cell in ws[ws.max_row]:  # Total row
        cell.font = bold_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=13):
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
        institute_condition = "AND e.custom_section = %s"
        params = (from_date, to_date, dept)
    elif institute and dept:
        institute_condition = "AND e.custom_institute_name = %s AND e.custom_section = %s"
        params = (from_date, to_date, institute, dept)
    else:
        institute_condition = ""
        params = (from_date, to_date)

    # Fetch basic salary data
    # basic_data = frappe.db.sql("""
    #     SELECT 
    #         e.custom_section AS department, 
    #         SUM(
    #             CASE 
    #                 WHEN (e.date_of_joining BETWEEN s.start_date AND s.end_date) or (e.relieving_date BETWEEN s.start_date AND s.end_date)
    #                 THEN ROUND((s.custom_total / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
    #                 ELSE s.custom_total
    #             END
    #         ) AS total_basic_amount
    #     FROM 
    #         `tabSalary Slip` s
    #     LEFT JOIN 
    #         `tabEmployee` e ON s.employee = e.name
    #     WHERE 
    #         s.docstatus != 2
    #         AND s.start_date BETWEEN %s AND %s
    #         AND e.custom_section IS NOT NULL
    #         AND e.custom_section != ''
    #         {institute_condition}
    #     GROUP BY 
    #         e.custom_section
    # """.format(institute_condition=institute_condition), 
    # params, as_dict=True)
   
    basic_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(
                CASE 
                    WHEN e.custom_visiting_facility = 1 THEN s.gross_pay
                    
                    WHEN (e.date_of_joining BETWEEN s.start_date AND s.end_date) 
                    OR (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    THEN ROUND((s.custom_total / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
                    
                    ELSE s.custom_total
                END
            ) AS total_basic_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.docstatus != 2
            AND s.start_date BETWEEN %s AND %s
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
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
            s.docstatus != 2
            AND cs.salary_component = 'Provident Fund' 
            AND s.start_date BETWEEN %s AND %s
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
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
            s.docstatus != 2
            AND cs.salary_component = 'Professional Tax' 
            AND s.start_date BETWEEN %s AND %s
                              AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    esi_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_esi_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.docstatus != 2
            AND cs.salary_component = 'ESI' 
            AND s.start_date BETWEEN %s AND %s
                             AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    tds_data = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_tds_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.docstatus != 2
            AND cs.salary_component = 'TDS' 
            AND s.start_date BETWEEN %s AND %s
                             AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
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
            s.docstatus != 2
            AND cs.salary_component = 'Loan' 
            AND s.start_date BETWEEN %s AND %s
                         AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    emp_adv = frappe.db.sql("""
        SELECT 
            e.custom_section AS department, 
            SUM(cs.amount) AS total_advance_amount
        FROM 
            `tabSalary Slip` s
        LEFT JOIN 
            `tabSalary Detail` cs ON s.name = cs.parent
        LEFT JOIN 
            `tabEmployee` e ON s.employee = e.name
        WHERE 
            s.docstatus != 2
            AND cs.salary_component = 'Employee Advance' 
            AND s.start_date BETWEEN %s AND %s
                            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
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
            s.docstatus != 2
            AND cs.salary_component = 'Other Deductions' 
            AND s.start_date BETWEEN %s AND %s
                                     AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
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
            s.docstatus != 2
            AND s.start_date BETWEEN %s AND %s
                                   AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
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
            s.docstatus != 2
            AND s.start_date BETWEEN %s AND %s
                                       AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
        GROUP BY 
            e.custom_section
    """.format(institute_condition=institute_condition), 
    params, as_dict=True)

    lop_data = frappe.db.sql("""
                SELECT 
                    e.custom_section AS department,
                    SUM(s.custom_lop_amount) AS total_lop
                FROM
                    `tabSalary Slip` s
                LEFT JOIN
                    `tabEmployee` e ON s.employee = e.name
                WHERE
                    s.docstatus != 2
                    AND s.start_date BETWEEN %s AND %s
                    AND e.custom_section IS NOT NULL
                    AND e.custom_section != ''
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
    # lop_data = frappe.db.sql("""
    #     SELECT 
    #         e.custom_section AS department, 
    #         SUM(s.gross_pay) AS tot_gross
            
    #     FROM 
    #         `tabSalary Slip` s
    #     LEFT JOIN 
    #         `tabEmployee` e ON s.employee = e.name
    #     WHERE 
    #         s.docstatus != 2
    #         AND s.start_date BETWEEN %s AND %s
    #                          AND e.custom_section IS NOT NULL
    #         AND e.custom_section != ''
    #         {institute_condition}
    #     GROUP BY 
    #         e.custom_section
    # """.format(institute_condition=institute_condition), 
    # params, as_dict=True)

    # for item in lop_data:
    #     department = item['department']
    #     if department in data:
    #         data[department]['tot_gross'] = item['tot_gross']
    #     else:
    #         data[department] = {
    #             "department": department,
    #             "tot_gross": item['tot_gross']
    #         }
    for item in lop_data:
        department = item['department']
        if department in data:
            data[department]['lop_amount'] = item['total_lop']
        else:
            data[department] = {
                "department": department,
                "lop_amount": item['total_lop']
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

    for item in esi_data:
        department = item['department']
        if department in data:
            data[department]['total_esi_amount'] = item['total_esi_amount']
        else:
            data[department] = {
                "department": department,
                "total_esi_amount": item['total_esi_amount']
            }

    for item in tds_data:
        department = item['department']
        if department in data:
            data[department]['total_tds_amount'] = item['total_tds_amount']
        else:
            data[department] = {
                "department": department,
                "total_tds_amount": item['total_tds_amount']
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
    for item in emp_adv:
        department = item['department']
        if department in data:
            data[department]['total_advance_amount'] = item['total_advance_amount']
        else:
            data[department] = {
                "department": department,
                "total_advance_amount": item['total_advance_amount']
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
    

    # for item in net_payable_salary:
    #     department = item['department']
    #     # net_pay_rounded = math.floor(item['net_pay'] + 0.5)
    #     # net_pay_rounded = math.ceil(item['net_pay'])
    #     net_pay_rounded = int(item['net_pay'] + 0.5)

    #     if department in data:
    #         data[department]['net_pay'] = net_pay_rounded
    #     else:
    #         data[department] = {
    #             "department": department,
    #             "net_pay": net_pay_rounded
    #         }


    return list(data.values())





@frappe.whitelist()
def get_consolidated_statement_data(from_date, to_date, institute=None, dept=None):
    args = {
        "from_date": from_date,
        "to_date": to_date,
        "institute_name": institute,
        "dept": dept,
        
    }

    return get_data(args)


def get_consolidated_statement_data_for_jinja(doc):
    from_date = getattr(doc, "from_date", None)
    to_date = getattr(doc, "to_date", None)
    institute = getattr(doc, "institute_name", None)
    dept = getattr(doc, "custom_section", None)

    if not from_date or not to_date:
        return {} 

    return get_consolidated_statement_data(from_date, to_date, institute, dept)

