# Copyright (c) 2025, Abdulla PI and contributors

# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document


class GeneralReceipt(Document):

    def after_insert(self):
        if not self.reciept_number:
            rec_list = frappe.db.get_all(
                "General Receipt",
                {
                    "reciept_number": ["!=", ""],
                    "docstatus": ["!=", 2]
                },
                ["reciept_number"]
            )

            pattern = re.compile(r"^G-\d{6}$")
            max_num = 0

            if rec_list:
                for rec in rec_list:
                    receipt_number = rec["reciept_number"]

                    if pattern.match(receipt_number):
                        num_part = int(receipt_number[2:])

                        if num_part > max_num:
                            max_num = num_part

                new_receipt_number = f"G-{str(max_num + 1).zfill(6)}"
            else:
                new_receipt_number = "G-000001"

            self.reciept_number = new_receipt_number

        else:
            if frappe.db.exists(
                "General Receipt",
                {
                    "reciept_number": self.reciept_number,
                    "name": ["!=", self.name],
                    "docstatus": ["!=", 2]
                }
            ):
                rec_list = frappe.db.get_all(
                    "General Receipt",
                    {
                        "reciept_number": ["!=", ""],
                        "name": ["!=", self.name],
                        "docstatus": ["!=", 2]
                    },
                    ["reciept_number"]
                )

                pattern = re.compile(r"^G-\d{6}$")
                max_num = 0

                if rec_list:
                    for rec in rec_list:
                        receipt_number = rec["reciept_number"]

                        if pattern.match(receipt_number):
                            num_part = int(receipt_number[2:])

                            if num_part > max_num:
                                max_num = num_part

                    new_receipt_number = f"G-{str(max_num + 1).zfill(6)}"
                else:
                    new_receipt_number = "G-000001"

                self.reciept_number = new_receipt_number
                self.db_set("reciept_number", self.reciept_number)


@frappe.whitelist()
def get_rec_no():
    rec_list = frappe.db.get_all(
        "General Receipt",
        {
            "reciept_number": ["!=", ""],
            "docstatus": ["!=", 2]
        },
        ["reciept_number"]
    )

    pattern = re.compile(r"^G-\d{6}$")
    max_num = 0

    if rec_list:
        for rec in rec_list:
            receipt_number = rec["reciept_number"]

            if pattern.match(receipt_number):
                num_part = int(receipt_number[2:])

                if num_part > max_num:
                    max_num = num_part

        new_receipt_number = f"G-{str(max_num + 1).zfill(6)}"
    else:
        new_receipt_number = "G-000001"

    return new_receipt_number