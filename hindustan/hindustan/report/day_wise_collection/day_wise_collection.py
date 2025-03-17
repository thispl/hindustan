# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_columns():
    return [
        _("Date") + ":Date:120",
        _("Bill ID") + ":Data:200",
        _("Student Name") + ":Link/Student:150",
        _("Program") + ":Data:150",
        _("Academic Term") + ":Data:120",
        _("Amount") + ":Currency:120",
        _("Payment Mode") + ":Data:150"
    ]

def get_data(filters):
    condition = add_filters(filters)

    registration_sql, registration_params = registration(condition)
    admission_sql, admission_params = admission(condition)
    prospectus_sql, prospectus_params = prospectus(condition)
    fees_collection_sql, fees_collection_params = fees_collection(condition)
    received_amount_sql, received_amount_params = received_amounts(condition)

    registration_data = frappe.db.sql(registration_sql, registration_params, as_dict=True)
    admission_data = frappe.db.sql(admission_sql, admission_params, as_dict=True)
    prospectus_data = frappe.db.sql(prospectus_sql, prospectus_params, as_dict=True)
    fees_collection_data = frappe.db.sql(fees_collection_sql, fees_collection_params, as_dict=True)
    received_amount_data = frappe.db.sql(received_amount_sql, received_amount_params, as_dict=True)
    
    data = []
    
    if (filters.get("bill_wise") == "Registration" or filters.get("bill_wise") == None) and (filters.get("student")== None):
        for reg in registration_data:
            if reg["amount_paid"] > 0:
                data.append([
                    reg["payment_date"],
                    reg["name"],
                    reg["student_name"],
                    reg["program"],
                    reg['academic_term'],
                    reg["amount_paid"],
                    reg["payment_mode"]
                ])

    if filters.get("bill_wise") == "Admission" or filters.get("bill_wise") == None:
        for amd in admission_data:
            if amd["paid_amount"] > 0:
                data.append([
                    amd["admission_date"],
                    amd["name"],
                    amd["student_name"],
                    amd["program"],
                    amd["batch__semester"],
                    amd["paid_amount"],
                    amd["payment_mode"]
                ])
    
    if (filters.get("bill_wise") == "Prospectus" or filters.get("bill_wise") == None) and (filters.get("student")== None) and (filters.get("academic_term")== None):
        for pro in prospectus_data:
            if pro["paid_amount"] > 0:
                data.append([
                    pro["payment_date"],
                    pro["name"],
                    pro["student_name"],
                    pro["program"],
                    '',
                    pro["paid_amount"],
                    pro["payment_mode"]
                ]) 
    if filters.get("bill_wise") == "Fees Collection" or filters.get("bill_wise") == None:
        for collected_fee in fees_collection_data:
            if collected_fee['paying_amount'] > 0:
                data.append([
                    collected_fee["posting_date"],
                    collected_fee["name"],
                    collected_fee["student_name"],
                    collected_fee["program"],
                    collected_fee['academic_term'],
                    collected_fee['paying_amount'],
                    collected_fee['payment_mode']
                ])
    if filters.get("bill_wise") == "General Receipt" or filters.get("bill_wise") == None:
        for amount_received in received_amount_data:
            if amount_received['received_amount'] > 0:
                data.append([
                    amount_received["received_date"],
                    amount_received["name"],
                    amount_received["person_name"],
                    amount_received["program"],
                    "",
                    amount_received['received_amount'],
                    amount_received['mode']
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
        
    fee = filters.get("fee")
    
    return condition

def registration(condition):
    sql = """
        SELECT
            r.payment_date,
            r.name,
            r.student_name,
            r.program,
            r.academic_term,
            r.amount_paid,
            r.payment_mode
        FROM
            `tabRegistration` r
        WHERE
            r.docstatus = 1
            AND r.payment_date BETWEEN %s AND %s
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
    sql = """
        SELECT
            a.admission_date,
            a.name,
            a.student_name,
            a.program,
            a.batch__semester,
            a.paid_amount,
            a.payment_mode
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
    sql += " ORDER BY a.`admission_date` ASC"

    return sql, params

def prospectus(condition):
    sql = """
        SELECT
            p.payment_date,
            p.name,
            p.student_name,
            p.program,
            '',
            p.paid_amount,
            p.payment_mode
        FROM
            `tabProspectus` p
        WHERE
            p.docstatus = 1
            AND p.payment_date BETWEEN %s AND %s
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
            f.posting_date,
            f.name,
            f.student_name,
            f.program,
            f.academic_term,
            f.paying_amount,
            f.payment_mode
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
    if "academic_term" in condition:
        sql += " AND f.academic_term = %s"
        params.append(condition["academic_term"])

    sql += " ORDER BY f.`posting_date` ASC"
    
    return sql, params

def received_amounts(condition):
    sql = """
        SELECT
            r.received_date AS received_date,
            r.name AS name,
            r.recieved_person AS recieved_person,
            r.received_amount AS received_amount,
            r.mode AS mode,
            r.program AS program,
            rp.person_name AS person_name
        FROM
            `tabGeneral Receipt` r
        LEFT Join
            `tabReceiving Person` rp ON rp.name = r.recieved_person
        WHERE
            r.docstatus = 1
            AND r.received_date BETWEEN %s AND %s
    """
    params = [condition.get("received_date")[1][0], condition.get("received_date")[1][1]]

    # if "institution_name" in condition:
    #     sql += " AND f.institute = %s"
    #     params.append(condition["institution_name"])

    if "program" in condition:
        sql += " AND r.program = %s"
        params.append(condition["program"])

    # if "student" in condition:
    #     sql += " AND f.student = %s"
    #     params.append(condition["student"])

    # if "academic_year" in condition:
    #     sql += " AND f.academic_year = %s"
    #     params.append(condition["academic_year"])
        
    # if "academic_term" in condition:
    #     sql += " AND f.academic_term = %s"
    #     params.append(condition["academic_term"])

    sql += " ORDER BY r.`received_date` ASC"
    
    return sql, params