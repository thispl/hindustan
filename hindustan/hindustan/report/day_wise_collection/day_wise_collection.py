# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from frappe.utils.data import add_days, add_years, today,getdate
def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_columns():
    return [
        _("Date") + ":Data:120",
        _("Registration No") + ":Data:200",
        _("Admission No") + ":Data:200",
        _("Receipt No") + ":Data:200",
        _("Name") + ":Link/Student:150",
        _("Program") + ":Data:150",
        _("Academic Term") + ":Data:120",
         _("Semester") + ":Data:120",
        _("Amount") + ":Currency:120",
        _("Payment Mode") + ":Data:150",
        _("Reference ID") + ":Data:150"
    ]

def get_data(filters):
    condition = add_filters(filters)

    registration_sql, registration_params = registration(condition)
    admission_sql, admission_params = admission(condition)
    prospectus_sql, prospectus_params = prospectus(condition)
    fees_collection_sql, fees_collection_params = fees_collection(condition)
    received_amount_sql, received_amount_params = received_amounts(condition)
    add_amt_sql,add_params=add_collection(condition)
    registration_data = frappe.db.sql(registration_sql, registration_params, as_dict=True)
    admission_data = frappe.db.sql(admission_sql, admission_params, as_dict=True)
    prospectus_data = frappe.db.sql(prospectus_sql, prospectus_params, as_dict=True)
    fees_collection_data = frappe.db.sql(fees_collection_sql, fees_collection_params, as_dict=True)
    received_amount_data = frappe.db.sql(received_amount_sql, received_amount_params, as_dict=True)
    add_collection_data=frappe.db.sql(add_amt_sql, add_params, as_dict=True)
    data = []
    
    if (filters.get("bill_wise") == "Registration" or filters.get("bill_wise") == None) and (filters.get("student")== None) and filters.get("admission") is None:
        for reg in registration_data:
            pay_date = reg["date"].strftime("%d-%m-%Y")
            payment_date=str(pay_date)
            frappe.errprint(pay_date)
            if reg["amount_paid"] > 0:
                sem=frappe.db.get_value('Academic Term',{'name':reg['academic_term']},['custom_semester'])
                if not sem:
                    sem=0
                if reg['payment_mode']=="DD":
                    payment_id=reg['dd_number']
                elif reg['payment_mode']=="Cheque":
                    payment_id=reg['cheque_number']
                elif reg['payment_mode']=="Online Transfer":
                    payment_id=reg['reference_number']    
                else:
                    payment_id=''    
                data.append([      
                    pay_date,
                    reg["name"],
                    '',
                    reg['receipt_number'],
                    reg["student_name"],
                    reg["program"],
                    reg['academic_term'],
                    sem,
                    reg["amount_paid"],
                    reg["payment_mode"],
                    payment_id
                    # reg['reference_number'] 
                ])

    if filters.get("bill_wise") == "Admission" or filters.get("bill_wise") == None:
        for amd in admission_data:
            add_date=amd["admission_date"]
            if add_date:
                add_date_str = add_date.strftime('%Y-%m-%d')
                add_date_str = datetime.strptime(add_date_str, "%Y-%m-%d") 
                formatted_add_date = add_date_str.strftime("%d-%m-%Y")
            else:
                formatted_add_date=''
            if amd["paid_amount"] > 0:
                batch=frappe.db.get_value('Academic Term',{'name':amd["batch__semester"]},['custom_semester'])
                if not batch:
                    batch=0
                if amd['payment_mode']=="DD":
                    payment_id=amd['dd_number']
                elif reg['payment_mode']=="Cheque":
                    payment_id=amd['cheque_number']
                elif amd['payment_mode']=="Online Transfer":
                    payment_id=amd['reference_number']    
                else:
                    payment_id=''    
                data.append([       
                    formatted_add_date,
                    amd["name"],
                    amd["name"],
                    '',
                    amd["student_name"],
                    amd["program"],
                    amd["batch__semester"],
                    batch,
                    amd["paid_amount"],
                    amd["payment_mode"],
                    # amd['reference_number'] 
                    payment_id
                ])
    
    if (filters.get("bill_wise") == "Prospectus" or filters.get("bill_wise") == None) and (filters.get("student")== None) and (filters.get("academic_term")== None and filters.get("admission") is None):
        for pro in prospectus_data:
            if pro["paid_amount"] > 0:
                
                pros_date=pro["issue_date"]
                if pros_date:
                    pros_date_str = pros_date.strftime('%Y-%m-%d')
                    pros_date_str = datetime.strptime(pros_date_str, "%Y-%m-%d") 
                    formatted_pros_date = pros_date_str.strftime("%d-%m-%Y")
                else:
                    formatted_pros_date=''
                if pro['payment_mode']=="DD":
                    payment_id=pro['dd_number']
                elif pro['payment_mode']=="Cheque":
                    payment_id=pro['cheque_number']
                elif pro['payment_mode']=="Online Transfer":
                    payment_id=pro['reference_number']    
                else:
                    payment_id=''    
                data.append([                   
                    formatted_pros_date,
                    pro["name"],
                    '',
                    pro['receipt_number'],
                    pro["student_name"],
                    pro["program"],
                    '',
                    '',
                    pro["paid_amount"],
                    pro["payment_mode"],
                    payment_id
                    # pro['reference_number'] 
                ]) 
    if filters.get("bill_wise") == "Fees Collection" or filters.get("bill_wise") == None and filters.get("admission") is None:
        for collected_fee in fees_collection_data:
            if collected_fee['paying_amount'] > 0:
                # payment_id = collected_fee['reference_number']
                sem1=frappe.db.get_value('Academic Term',{'name':collected_fee['academic_term']},['custom_semester'])
                if not sem1:
                    sem1=0
                fc_date=collected_fee["posting_date"]
                if fc_date:
                    fc_date_str = fc_date.strftime('%Y-%m-%d')
                    fc_date_str = datetime.strptime(fc_date_str, "%Y-%m-%d") 
                    formatted_fc_date = fc_date_str.strftime("%d-%m-%Y")
                else:
                    formatted_fc_date=''
                if collected_fee['payment_mode']=="DD":
                    payment_id=collected_fee['dd_number']
                elif collected_fee['payment_mode']=="Cheque":
                    payment_id=collected_fee['cheque_number']
                elif collected_fee['payment_mode']=="Online Transfer":
                    payment_id=collected_fee['reference_number']    
                else:
                    payment_id=''
                   
                data.append([
                    formatted_fc_date,
                    collected_fee["name"],
                    collected_fee["admission"],
                    collected_fee["receipt_number"],
                    collected_fee["student_name"],
                    collected_fee["program"],
                    collected_fee['academic_term'],
                    sem1,
                    collected_fee['paying_amount'],
                    collected_fee['payment_mode'],
                    payment_id
                    # collected_fee['reference_number'] 
                ])
    if (filters.get("bill_wise") == "General Receipt" or filters.get("bill_wise") is None) and filters.get("admission") is None:
        frappe.log_error("Reporting","filter")
        # if amount_received['is_student']==1:
        for amount_received in received_amount_data:
            if amount_received['received_amount'] > 0:
                gr_date=amount_received["received_date"]
                if gr_date:
                    gr_date_str = gr_date.strftime('%Y-%m-%d')
                    gr_date_str = datetime.strptime(gr_date_str, "%Y-%m-%d") 
                    formatted_gr_date = gr_date_str.strftime("%d-%m-%Y")
                else:
                    formatted_gr_date=''
                
                if amount_received['mode']=="DD":
                    payment_id=amount_received['dd_number']
                elif amount_received['mode']=="Cheque":
                    payment_id=amount_received['cheque_number']
                elif amount_received['mode']=="Online Transfer":
                    payment_id=amount_received['reference_number']    
                else:
                    payment_id=''
                data.append([
                    formatted_gr_date,
                    amount_received["name"],
                    amount_received["admission"],
                    amount_received["reciept_number"],

                    amount_received["person_name"],
                    amount_received["program"],
                    "",
                    '',
                    amount_received['received_amount'],
                    amount_received['mode'],
                    payment_id
                    # amount_received['reference_number'] 
                ])
    if filters.get("bill_wise") == "General Receipt" and filters.get("admission"):
        for amount_received in received_amount_data:
            if amount_received['received_amount'] > 0:
                gr_date=amount_received["received_date"]
                if gr_date:
                    gr_date_str = gr_date.strftime('%Y-%m-%d')
                    gr_date_str = datetime.strptime(gr_date_str, "%Y-%m-%d") 
                    formatted_gr_date = gr_date_str.strftime("%d-%m-%Y")
                else:
                    formatted_gr_date=''
                

                data.append([
                    formatted_gr_date,
                    amount_received["name"],
                    amount_received["admission"],
                    amount_received["reciept_number"],

                    amount_received["person_name"],
                    amount_received["program"],
                    "",
                    '',
                    amount_received['received_amount'],
                    amount_received['mode'],
                    amount_received['reference_number'] 
                ])
    if filters.get("bill_wise") is None and filters.get("admission"):
        for amount_received in received_amount_data:
            if amount_received['received_amount'] > 0 and amount_received['admission']==filters.get("admission"):
                gr_date=amount_received["received_date"]
                if gr_date:
                    gr_date_str = gr_date.strftime('%Y-%m-%d')
                    gr_date_str = datetime.strptime(gr_date_str, "%Y-%m-%d") 
                    formatted_gr_date = gr_date_str.strftime("%d-%m-%Y")
                else:
                    formatted_gr_date=''
                

                data.append([
                    formatted_gr_date,
                    amount_received["name"],
                    '',
                    amount_received["reciept_number"],

                    amount_received["person_name"],
                    amount_received["program"],
                    "",
                    '',
                    amount_received['received_amount'],
                    amount_received['mode'],
                    amount_received['reference_number'] 
                ])
    # elif (filters.get("bill_wise") == "Fees Collection" or filters.get("bill_wise") == None) and (filters.get("student") != None):
    #     for collected_fee in fees_collection_data:
    #         data.append([
    #             collected_fee["posting_date"],
    #             collected_fee["name"],
    #             collected_fee["student_name"],
    #             collected_fee["program"],
    #             collected_fee['academic_term'],
    #             collected_fee['paying_amount'],
    #             collected_fee['payment_mode']
    #         ])
    # for fee_record in fee_data:
    #     data.append([
    #         fee_record["fee_date"],  # Assuming there's a 'fee_date' field
    #         fee_record["parent_name"],
    #         fee_record["student_name"],
    #         fee_record["program"],
    #         '',
    #         fee_record["amount"],
    #         fee_record["payment_mode"]
    #     ])

    return data

def add_filters(filters):
    condition = {
        "docstatus": ["!=", 2],
        "admission_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
        "payment_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
        "payment_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
        "posting_date":["between", [filters.get("from_date"), filters.get("to_date")]],
        "received_date":["between", [filters.get("from_date"), filters.get("to_date")]],
    }

    if filters.get("institution"):
        condition["institution_name"] = filters.get("institution")

    if filters.get("program_wise"):
        condition["program"] = filters.get("program_wise")

    if filters.get("student"):
        condition["student"] = filters.get("student")

    if filters.get("academic_wise"):
        condition["academic_year"] = filters.get("academic_wise")
        
    if filters.get("academic_term"):
        condition["academic_term"] = filters.get("academic_term")

    if filters.get("admission"):
        condition["admission"] = filters.get("admission")
        
    fee = filters.get("fee")
    
    return condition

def registration(condition):
    sql = """
        SELECT
            r.receipt_number,
            r.date,
            r.payment_date,
            r.name,
            r.student_name,
            r.program,
            r.academic_term,
            r.amount_paid,
            r.payment_mode,
            r.cheque_number,
            r.dd_number,
            r.reference_number
        FROM
            `tabRegistration` r
        WHERE
            r.docstatus = 1
            AND r.date BETWEEN %s AND %s
    """
    params = [condition.get("payment_date")[1][0], condition.get("payment_date")[1][1]]

    if "institution_name" in condition:
        sql += " AND r.institution_name = %s"
        params.append(condition["institution_name"])

    if "program" in condition:
        sql += " AND r.program = %s"
        params.append(condition["program"])

    # if "student_name" in condition:
    #     sql += " AND r.student_name = %s"
    #     params.append(condition["student_name"])

    if "academic_year" in condition:
        sql += " AND r.academic_year = %s"
        params.append(condition["academic_year"])
    if "academic_term" in condition:
        sql += " AND r.academic_term = %s"
        params.append(condition["academic_term"])
    sql += " ORDER BY r.`payment_date` ASC"

    return sql, params

def admission(condition):
    # sql = """
    #     SELECT
    #         a.admission_date,
    #         a.name,
    #         a.student_name,
    #         a.program,
    #         a.batch__semester,
    #         a.paid_amount,
    #         a.payment_mode
    #     FROM
    #         `tabAdmission` a
    #     WHERE
    #         a.docstatus = 1
    #         AND a.admission_date BETWEEN %s AND %s
    #     ORDER BY a.name,a.admission_date ASC
    # """
    sql = """
        SELECT
            a.admission_date,
            a.name,
            a.student_name,
            a.program,
            a.batch__semester,
            a.paid_amount,
            a.payment_mode,
            a.cheque_number,
            a.dd_number,
            a.reference_number
        FROM
            `tabAdmission` a
        WHERE
            a.docstatus = 1
            AND a.admission_date BETWEEN %s AND %s
    """
    params = [condition.get("admission_date")[1][0], condition.get("admission_date")[1][1]]

    if "institution_name" in condition:
        sql += " AND a.institution_name = %s"
        params.append(condition["institution_name"])

    if "program" in condition:
        sql += " AND a.program = %s"
        params.append(condition["program"])

    if "student" in condition:
        sql += " AND a.student = %s"
        params.append(condition["student"])

    if "academic_year" in condition:
        sql += " AND a.academic_year = %s"
        params.append(condition["academic_year"])
    if "academic_term" in condition:
        sql += " AND a.batch__semester = %s"
        params.append(condition["academic_term"])
    if "admission" in condition:
        sql += " AND a.name = %s"
        params.append(condition["admission"])
    # sql += " ORDER BY a.`admission_date` ASC"

    return sql, params

def prospectus(condition):
    sql = """
        SELECT
            p.receipt_number,
            p.issue_date,
            p.payment_date,
            p.name,
            p.student_name,
            p.program,
            '',
            p.paid_amount,
            p.payment_mode,
            p.cheque_number,
            p.dd_number,
            p.reference_number
        FROM
            `tabProspectus` p
        WHERE
            p.docstatus = 1
            AND p.issue_date BETWEEN %s AND %s
    """
    params = [condition.get("payment_date")[1][0], condition.get("payment_date")[1][1]]

    if "institution_name" in condition:
        sql += " AND p.institution_name = %s"
        params.append(condition["institution_name"])

    if "program" in condition:
        sql += " AND p.program = %s"
        params.append(condition["program"])

    # if "student_name" in condition:
    #     sql += " AND p.student_name = %s"
    #     params.append(condition["student_name"])

    if "academic_year" in condition:
        sql += " AND p.academic_year = %s"
        params.append(condition["academic_year"])


    sql += " ORDER BY p.`payment_date` ASC"

    return sql, params


def fees_collection(condition):
    sql = """
        SELECT
            f.receipt_number,
            f.posting_date,
            f.name,
            f.admission,
            f.student_name,
            f.program,
            f.academic_term,
            f.paying_amount,
            f.payment_mode,
            f.admission,
            f.reference_number,
            f.dd_number,
            f.cheque_number
        FROM
            `tabFees Collection` f
        WHERE
            f.docstatus = 1
            AND f.posting_date BETWEEN %s AND %s
    """
    params = [condition.get("posting_date")[1][0], condition.get("posting_date")[1][1]]

    if "institution_name" in condition:
        sql += " AND f.institute = %s"
        params.append(condition["institution_name"])

    if "program" in condition:
        sql += " AND f.program = %s"
        params.append(condition["program"])

    if "student" in condition:
        sql += " AND f.student = %s"
        params.append(condition["student"])

    if "academic_year" in condition:
        sql += " AND f.academic_year = %s"
        params.append(condition["academic_year"])

    if "admission" in condition:
        sql += " AND f.admission = %s"
        params.append(condition["admission"])

    if "academic_term" in condition:
        sql += " AND f.academic_term = %s"
        params.append(condition["academic_term"])

    # sql += " ORDER BY f.`posting_date` ASC"
    
    return sql, params

def received_amounts(condition):
    sql = """
        SELECT
            r.reciept_number,
            r.reference_number,
            r.posting_date AS received_date,
            r.name AS name,
            r.recieved_person AS recieved_person,
            r.received_amount AS received_amount,
            r.mode AS mode,
            r.program AS program,
            rp.person_name AS person_name,
            rp.is_student AS is_student,
            rp.student AS student,
            r.admission AS admission,
            r.cheque_number,
            r.dd_number
        FROM
            `tabGeneral Receipt` r
        LEFT Join
            `tabReceiving Person` rp ON rp.name = r.recieved_person
        WHERE
            r.docstatus = 1
            AND r.posting_date BETWEEN %s AND %s
    """
    params = [condition.get("received_date")[1][0], condition.get("received_date")[1][1]]

    # if "institution_name" in condition:
    #     sql += " AND f.institute = %s"
    #     params.append(condition["institution_name"])

    if "program" in condition:
        sql += " AND r.program = %s"
        params.append(condition["program"])

    if "student" in condition:
        sql += " AND r.student = %s"
        params.append(condition["student"])

    # if "academic_year" in condition:
    #     sql += " AND f.academic_year = %s"
    #     params.append(condition["academic_year"])
        
    # if "academic_term" in condition:
    #     sql += " AND f.academic_term = %s"
    #     params.append(condition["academic_term"])

    sql += " ORDER BY r.`received_date` ASC"
    
    return sql, params

# def add_collection(condition):
#     sql = """
#         SELECT
#             f.receipt_number,
#             f.posting_date,
#             f.name,
#             f.admission,
#             f.student_name,
#             f.program,
#             f.academic_term,
#             f.paying_amount,
#             f.payment_mode,
#             f.admission
#         FROM
#             `tabFees Collection` f
#         WHERE
#             f.docstatus = 1
#             AND f.posting_date BETWEEN %s AND %s
#     """
#     params = [condition.get("posting_date")[1][0], condition.get("posting_date")[1][1]]


#     if "admission" in condition:
#         sql += " AND f.admission = %s"
#         params.append(condition["admission"])
#     if "program" in condition:
#         sql += " AND f.program = %s"
#         params.append(condition["program"])

#     if "academic_year" in condition:
#         sql += " AND f.academic_year = %s"
#         params.append(condition["academic_year"])
#     if "academic_term" in condition:
#         sql += " AND f.academic_term = %s"
#         params.append(condition["academic_term"])
   
    
#     return sql, params

def add_collection(condition):
    sql = """
        SELECT
            f.receipt_number,
            f.posting_date,
            f.name,
            f.admission,
            f.student_name,
            f.program,
            f.academic_term,
            f.paying_amount,
            f.payment_mode,
            f.admission,
            f.reference_number
        FROM
            `tabFees Collection` f
        WHERE
            f.docstatus = 1
            AND f.posting_date BETWEEN %s AND %s
    """

    # Safely extract date range
    from_date = condition.get("posting_date", ["", ["", ""]])[1][0]
    to_date = condition.get("posting_date", ["", ["", ""]])[1][1]
    params = [from_date, to_date]

    # Additional filters
    if condition.get("admission"):
        sql += " AND f.admission = %s"
        params.append(condition["admission"])

    if condition.get("program"):
        sql += " AND f.program = %s"
        params.append(condition["program"])

    if condition.get("academic_year"):
        sql += " AND f.academic_year = %s"
        params.append(condition["academic_year"])

    if condition.get("academic_term"):
        sql += " AND f.academic_term = %s"
        params.append(condition["academic_term"])

    return sql, params
