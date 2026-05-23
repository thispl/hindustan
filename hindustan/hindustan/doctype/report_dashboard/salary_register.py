import frappe
from frappe.model.document import Document
import math
import frappe
from io import BytesIO
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment, Border, Side,Font
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP


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
        'G': 20, 'H': 20, 'I': 20, 'J': 20, 'K': 25,'L':20,'M':20,'N':20,'O':20,'P':20,'Q':20,'R':20,'S':20
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    month_year = from_date.strftime('%B %Y')
    month_year=str(month_year).upper()
    ws.append([f"SALARY REGISTER FOR THE MONTH OF - {month_year}"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=19)
    ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
    section_name = args.get("dept")
    if section_name:
        section_display = f"SECTION : {section_name.upper()}"
    else:
        section_display = "SECTION : ALL SECTIONS"
    ws.append([section_display])
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=19)
    ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(row=2, column=1).font = Font(bold=True)

    sub_header = [
        "Name", "No:of Days", "Basic", "DA", "HRA", "Med",
        "Conv", "Allow", "Gross Salary", "Pay Loss", "PF","P Tax","ESI","TDS","Loan","Adv","Other Deductions","Total Ded","Nett Sal"
    ]
    ws.append(sub_header)
    bold_font = Font(bold=True)
    for cell in ws[3]:  # Header row is the second row
        cell.font = bold_font
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=19):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center') 

    data=get_data_for_sr(args)
    totals = [0] * 17
    net_pay_total = Decimal("0") 
    for employee_name, employee_data in data.items():
        # lop=employee_data.get("gross_pay", "0")-employee_data.get("lop_amount", "0")
        lop = employee_data.get("lop_amount", 0) or 0
        tot_deductions=float(employee_data.get("total_deductions", 0) or 0)
        if lop<0:
            lop=0
        tot_deduction = tot_deductions + lop
        
        basic_amount = float(employee_data.get("basic_amount", 0) or 0)

        # net_pay = Decimal(str(employee_data.get("net_pay", 0) or 0))
        net_pay = Decimal(str(employee_data.get("net_pay", 0) or 0))

        net_pay = net_pay.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
  
        row = [
            employee_name,
            employee_data.get("no_of_days", "0"),
            basic_amount,
            employee_data.get("da_amount", "0"),
            employee_data.get("hra_amount", "0"),
            employee_data.get("med_amount", "0"),
            employee_data.get("convey_amount", "0"),
            employee_data.get("allow_amount", "0"),
            employee_data.get("gross_pay", "0"),
            round(lop),
            employee_data.get("pf_amount", "0"),
            employee_data.get("ptax_amount", "0"),
            employee_data.get("esi_amount", "0"),
            employee_data.get("tds_amount", "0"),
            employee_data.get("loan_amount", "0"),
            employee_data.get("adv_amount", "0"),
            employee_data.get("other_deductions", "0"),
            # employee_data.get("total_deductions", "0"),
            round(tot_deduction),
            # employee_data.get("net_pay", "0")
            format(net_pay, '.2f')
        ]
        
        ws.append(row)
    #     for i in range(1, 19):  
    #         totals[i-1] += float(row[i]) if row[i] else 0
    # totals_row = ["Total"] + [str(total) for total in totals]  


        for i in range(1, 18): 
            totals[i-1] += float(row[i]) if row[i] else 0
        # net_pay_total += float(row[18]) if row[18] else 0
        net_pay_total += net_pay
    # totals_row = ["Total"] + [str(total) for total in totals]  
    # totals_row = ["Total"] + [str(int(total)) for total in totals] + [str(round(net_pay_total))]
    totals_row = (
    ["Total"] +
    [str(int(total)) for total in totals] +
    [format(net_pay_total, '.2f')]
)

    ws.append(totals_row)
    ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=2)
    total_cell = ws.cell(row=ws.max_row, column=1)  # This is the merged cell (SI NO)
    total_cell.alignment = Alignment(horizontal='center', vertical='center')
    for cell in ws[ws.max_row]:  # Total row
        cell.font = bold_font
        
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=19):
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
        institute_condition = "AND e.custom_section = %s"
        params = (from_date, to_date, dept)
    elif institute and dept:
        institute_condition = "AND e.custom_institute_name = %s AND e.custom_section = %s"
        params = (from_date, to_date, institute, dept)
    else:
        institute_condition = ""
        params = (from_date, to_date)
    queries = {
        "no_of_days": """
            SELECT e.name AS employee_name, s.payment_days AS payment_days,e.employee_name as emp, s.custom_visiting_facility
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        # "basic_amount": """
        #     SELECT e.name AS employee_name, 
        #         s.salary_structure,
        #         CASE 
        #             WHEN (
        #                 (e.relieving_date BETWEEN s.start_date AND s.end_date)
        #                 OR
        #                 (e.date_of_joining BETWEEN s.start_date AND s.end_date)
        #                 )
        #                 AND s.total_working_days > 0
        #             THEN ROUND((s.custom_basic / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
        #             ELSE ROUND(s.custom_basic)
        #         END AS basic_amount,
        #         e.employee_name as emp,
        #         s.name as slip_name,
        #         s.custom_total_hours as Hours
        #     FROM `tabSalary Slip` s
        #     LEFT JOIN `tabEmployee` e ON s.employee = e.name
        #     LEFT JOIN `tabDesignation` d ON s.designation = d.name
        #     WHERE s.start_date BETWEEN %s AND %s 
        #     AND s.docstatus != 2
        #     AND e.custom_section IS NOT NULL
        #     AND e.custom_section != ''
        #     {institute_condition}
        #     ORDER BY
        # CASE 
        #     WHEN e.custom_section = 'OFFICE' THEN 
        #         CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
        #     WHEN e.custom_section = 'HEA' THEN 
        #         CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
        #     WHEN e.custom_section = 'HBS' THEN 
        #         CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
        #     WHEN e.custom_section = 'HAA' THEN 
        #         CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
        #     ELSE 9999
        # END,
        #     e.employee_name
        # """,
       
        "basic_amount": """
            SELECT 
                e.name AS employee_name,
                e.employee_name as emp,
                s.name as slip_name,
                s.custom_total_hours as Hours,
                s.custom_visiting_facility,

                CASE 
                    WHEN s.custom_visiting_facility = 1 THEN 
                        IFNULL((
                            SELECT SUM(sd.amount)
                            FROM `tabSalary Detail` sd
                            WHERE sd.parent = s.name
                            AND sd.salary_component = 'Basic VF'
                        ), 0)

                    WHEN (
                        (e.relieving_date BETWEEN s.start_date AND s.end_date)
                        OR
                        (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                    )
                    AND s.total_working_days > 0
                    THEN ROUND((s.custom_basic / s.total_working_days) * 
                        (s.payment_days + s.absent_days + s.leave_without_pay))

                    ELSE ROUND(s.custom_basic)
                END AS basic_amount

            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name

            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}

            ORDER BY
            CASE 
                WHEN e.custom_section = 'OFFICE' THEN 
                    CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
                WHEN e.custom_section = 'HEA' THEN 
                    CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
                WHEN e.custom_section = 'HBS' THEN 
                    CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
                WHEN e.custom_section = 'HAA' THEN 
                    CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
                ELSE 9999
            END,
            e.employee_name
        """,

        "da_amount": """
            SELECT e.name AS employee_name, 
            CASE 
                WHEN (
                    (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    OR
                    (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                )
                    AND s.total_working_days > 0
                THEN ROUND((s.custom_dearness_allowance / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
                ELSE ROUND(s.custom_dearness_allowance)
            END AS da_amount,
            e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "hra_amount": """
            SELECT e.name AS employee_name, 
            CASE 
                WHEN (
                    (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    OR
                    (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                )
                    AND s.total_working_days > 0
                THEN ROUND((s.custom_house_rent_allowance / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
                ELSE ROUND(s.custom_house_rent_allowance)
            END AS hra_amount,
            e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "med_amount": """
            SELECT e.name AS employee_name, 
            CASE 
                WHEN (
                    (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    OR
                    (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                )
                    AND s.total_working_days > 0
                THEN ROUND((s.custom_medical_allowance / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay) )
                ELSE ROUND(s.custom_medical_allowance)
            END AS med_amount,
            e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "convey_amount": """
            SELECT e.name AS employee_name, 
            CASE 
                WHEN (
                    (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    OR
                    (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                )
                    AND s.total_working_days > 0
                THEN ROUND((s.custom_conveyance_allowance / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
                ELSE ROUND(s.custom_conveyance_allowance)
            END AS convey_amount,
            e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "allow_amount": """
            SELECT e.name AS employee_name, 
            CASE 
                WHEN (
                    (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    OR
                    (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                )
                    AND s.total_working_days > 0
                THEN ROUND((IFNULL(s.custom_allowance,0) / s.total_working_days) * (s.payment_days + s.absent_days + s.leave_without_pay))
                ELSE ROUND(IFNULL(s.custom_allowance,0))
            END AS allow_amount,
            e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        # "gross_pay": """
        #     SELECT e.name AS employee_name, 
        #     CASE 
        #         WHEN (
        #             (e.relieving_date BETWEEN s.start_date AND s.end_date)
        #             OR
        #             (e.date_of_joining BETWEEN s.start_date AND s.end_date)
        #         )
        #             AND s.total_working_days > 0
        #         THEN ROUND((s.custom_total / s.total_working_days) *(s.payment_days + s.absent_days + s.leave_without_pay))
        #         ELSE ROUND(s.custom_total)
        #     END AS gross_pay,
        #     e.employee_name as emp
        #     FROM `tabSalary Slip` s
        #     LEFT JOIN `tabEmployee` e ON s.employee = e.name
        #     LEFT JOIN `tabDesignation` d ON s.designation = d.name
        #     WHERE s.start_date BETWEEN %s AND %s AND e.custom_section IS NOT NULL
        #     AND s.docstatus != 2
        #     AND e.custom_section != ''
        #     {institute_condition}
        #     ORDER BY
        # CASE 
        #     WHEN e.custom_section = 'OFFICE' THEN 
        #         CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
        #     WHEN e.custom_section = 'HEA' THEN 
        #         CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
        #     WHEN e.custom_section = 'HBS' THEN 
        #         CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
        #     WHEN e.custom_section = 'HAA' THEN 
        #         CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
        #     ELSE 9999
        # END,
        #     e.employee_name
        # """,
        
        "gross_pay": """
            SELECT e.name AS employee_name, 
            e.employee_name as emp,

            CASE 
                WHEN s.custom_visiting_facility = 1 THEN ROUND(s.gross_pay)

                WHEN (
                    (e.relieving_date BETWEEN s.start_date AND s.end_date)
                    OR
                    (e.date_of_joining BETWEEN s.start_date AND s.end_date)
                )
                AND s.total_working_days > 0
                THEN ROUND((s.custom_total / s.total_working_days) *
                    (s.payment_days + s.absent_days + s.leave_without_pay))

                ELSE ROUND(s.custom_total)
            END AS gross_pay

            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name

            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}

            ORDER BY
            CASE 
                WHEN e.custom_section = 'OFFICE' THEN 
                    CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
                WHEN e.custom_section = 'HEA' THEN 
                    CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
                WHEN e.custom_section = 'HBS' THEN 
                    CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
                WHEN e.custom_section = 'HAA' THEN 
                    CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
                ELSE 9999
            END,
            e.employee_name
        """,

        "lop_amount": """
            SELECT e.name AS employee_name, 
            s.custom_lop_amount AS lop_amount,
            e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "pf_amount": """
            SELECT e.name AS employee_name, cs.amount AS pf_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'Provident Fund' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "ptax_amount": """
            SELECT e.name AS employee_name, cs.amount AS ptax_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'Professional Tax' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "esi_amount": """
            SELECT e.name AS employee_name, cs.amount AS esi_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'ESI' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "tds_amount": """
            SELECT e.name AS employee_name, cs.amount AS tds_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'TDS' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "loan_amount": """
            SELECT e.name AS employee_name, cs.amount AS loan_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'Loan' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "adv_amount": """
            SELECT e.name AS employee_name, cs.amount AS adv_amount,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'Employee Advance' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "other_deductions": """
            SELECT e.name AS employee_name, cs.amount AS other_deductions,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabSalary Detail` cs ON s.name = cs.parent
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE cs.salary_component = 'Other Deductions' AND s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "total_deductions": """
            SELECT e.name AS employee_name, s.total_deduction AS total_deductions,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """,
        "net_pay": """
            SELECT e.name AS employee_name,  s.net_pay AS net_pay,e.employee_name as emp
            FROM `tabSalary Slip` s
            LEFT JOIN `tabEmployee` e ON s.employee = e.name
            LEFT JOIN `tabDesignation` d ON s.designation = d.name
            WHERE s.start_date BETWEEN %s AND %s 
            AND s.docstatus != 2
            AND e.custom_section IS NOT NULL
            AND e.custom_section != ''
            {institute_condition}
            ORDER BY
        CASE 
            WHEN e.custom_section = 'OFFICE' THEN 
                CASE WHEN IFNULL(d.custom_office_order_no, 0) = 0 THEN 9999 ELSE d.custom_office_order_no END
            WHEN e.custom_section = 'HEA' THEN 
                CASE WHEN IFNULL(d.custom_hea_order_no, 0) = 0 THEN 9999 ELSE d.custom_hea_order_no END
            WHEN e.custom_section = 'HBS' THEN 
                CASE WHEN IFNULL(d.custom_haeas_order_no, 0) = 0 THEN 9999 ELSE d.custom_haeas_order_no END
            WHEN e.custom_section = 'HAA' THEN 
                CASE WHEN IFNULL(d.custom_haa_order_no, 0) = 0 THEN 9999 ELSE d.custom_haa_order_no END
            ELSE 9999
        END,
            e.employee_name
        """
    }

    for key, query in queries.items():
        result = frappe.db.sql(query.format(institute_condition=institute_condition), 
                               params, 
                               as_dict=True)
        
        for row in result:
            employee_name = row["emp"]
            if employee_name not in data:
                data[employee_name] = {}

            if key == "no_of_days" and row.get("payment_days"):
                data[employee_name][key] = int(row["payment_days"])  
            else:
                data[employee_name][key] = row.get(key, "") 

    return data


@frappe.whitelist()
def get_salary_register_data(from_date, to_date, institute=None, dept=None):
    args = {
        "from_date": from_date,
        "to_date": to_date,
        "institute_name": institute,
        "dept": dept
    }

    return get_data_for_sr(args)


def get_salary_register_data_for_jinja(doc):
    from_date = getattr(doc, "from_date", None)
    to_date = getattr(doc, "to_date", None)
    institute = getattr(doc, "institute_name", None)
    dept = getattr(doc, "custom_section", None)

    if not from_date or not to_date:
        return {} 

    return get_salary_register_data(from_date, to_date, institute, dept)

