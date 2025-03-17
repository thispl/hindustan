# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PromotionAndTransfer(Document):
    # pass
    def on_submit(self):
        if self.promotion__transfer==1:
            if self.student_id__admission_id and not self.student_promotion:
                if not self.promotion_academic_year:
                    frappe.throw("Promotion Academic Year is required")
                elif not self.promotion_sem__batch:
                    frappe.throw("Promotion Sem / Batch is required")
                if self.promotion_academic_year and self.promotion_sem__batch:
                    student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
                    student.custom_promoted_academic_year=self.promotion_academic_year
                    student.custom_current_academic_term=self.promotion_sem__batch
                    student.save()
                    frappe.db.commit()
            if self.student_promotion and not self.student_id__admission_id:
                for i in self.student_promotion:
                    if not self.promotion_academic_year:
                        frappe.throw("Promotion Academic Year is required")
                    elif not self.promotion_sem__batch:
                        frappe.throw("Promotion Sem / Batch is required")
                    if self.student_promotion and self.promotion_sem__batch:
                        student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                        student.custom_promoted_academic_year=self.promotion_academic_year
                        student.custom_current_academic_term=self.promotion_sem__batch
                        student.save()
                        frappe.db.commit()
        elif self.transfer==1:
            if self.student_id__admission_id and not self.student_promotion:
                if not self.transfered_academic_year:
                    frappe.throw("Transfer Academic Year is required")
                elif not self.transfered_sembatch:
                    frappe.throw("Transfer Sem / Batch is required")
                if self.transfered_academic_year and self.transfered_sembatch:
                    student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
                    student.custom_transfered_academic_year=self.academic_year
                    student.custom_transfered_academic_term=self.batchsem
                    student.custom_transfered_institute=self.institute_name
                    student.custom_transfered_program=self.program
                    student.custom_academic_year=self.transfered_academic_year
                    student.custom_program=self.transfered_program
                    student.custom_current_academic_term=self.transfered_sembatch
                    student.custom_institute_name=self.transfered_institute_name
                    student.save()
                    frappe.db.commit()
            if self.student_promotion and not self.student_id__admission_id:
                for i in self.student_promotion:
                    if not self.transfered_academic_year:
                        frappe.throw("PromotionAndTransfer Academic Year is required")
                    elif not self.transfered_sembatch:
                        frappe.throw("PromotionAndTransfer Sem / Batch is required")
                    if self.student_promotion and self.transfered_sembatch:
                        student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                        student.custom_transfered_academic_year=self.transfered_academic_year
                        student.custom_transfered_academic_term=self.transfered_sembatch
                        student.custom_transfered_institute=self.transfered_institute_name
                        student.custom_transfered_program=self.transfered_program
                        student.custom_academic_year=self.transfered_academic_year
                        student.custom_program=self.transfered_program
                        student.custom_current_academic_term=self.transfered_sembatch
                        student.custom_institute_name=self.transfered_institute_name
                        student.save()
                        frappe.db.commit()
        elif self.promotion_and_transfer_via_assessment==1:
            if self.student_promotion:
                for i in self.student_promotion:
                    if not self.promotion_academic_year:
                        frappe.throw("Promotion Academic Year is required")
                    elif not self.promotion_sem__batch:
                        frappe.throw("Promotion Sem / Batch is required")
                    if self.student_promotion and self.promotion_sem__batch:
                        student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                        student.custom_promoted_academic_year=self.promotion_academic_year
                        student.custom_current_academic_term=self.promotion_sem__batch
                        student.save()
                        frappe.db.commit()


    def on_cancel(self):
        if self.promotion__transfer==1:
            if self.student_id__admission_id and not self.student_promotion:
                student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
                student.custom_promoted_academic_year=self.academic_year
                student.custom_current_academic_term=self.batchsem
                student.save()
                frappe.db.commit()
            if self.student_promotion and not self.student_id__admission_id:
                for i in self.student_promotion:
                    student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                    student.custom_promoted_academic_year=self.academic_year
                    student.custom_current_academic_term=self.batchsem
                    student.save()
                    frappe.db.commit()
        elif self.transfer==1:
            if self.student_id__admission_id and not self.student_promotion:
                if self.transfered_academic_year and self.transfered_sembatch:
                    student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
                    student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
                    student.custom_academic_year=self.academic_year
                    student.custom_program=self.program
                    student.custom_current_academic_term=self.batchsem
                    student.custom_institute_name=self.institute_name
                    student.custom_transfered_academic_year=""
                    student.custom_transfered_academic_term=""
                    student.custom_transfered_institute=""
                    student.custom_transfered_program=""
                    student.save()
                    frappe.db.commit()
            if self.student_promotion and not self.student_id__admission_id:
                for i in self.student_promotion:
                    if self.student_promotion and self.transfered_sembatch:
                        student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                        student.custom_transfered_academic_year=""
                        student.custom_transfered_academic_term=""
                        student.custom_transfered_institute=""
                        student.custom_transfered_program=""
                        student.save()
                        frappe.db.commit()
        elif self.promotion_and_transfer_via_assessment==1:
            if self.student_promotion:
                for i in self.student_promotion:
                    student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                    student.custom_promoted_academic_year=self.academic_year
                    student.custom_current_academic_term=self.batchsem
                    student.save()
                    frappe.db.commit()



@frappe.whitelist()
def get_student_details(inst_name,program,sem,year):
    data=[]
    students=frappe.db.get_all("Student",{"custom_academic_year":year,"custom_program":program,"custom_institute_name":inst_name,"custom_current_academic_term":sem},["*"])
    if students:
        for i in students:
            data.append([i.name,i.custom_program,i.custom_current_academic_term])
    else:
        frappe.msgprint("No Students found")
    return data

@frappe.whitelist()
def get_student_detail_assessment(program,academic_year,academic_term,institute_name):
    data=[]
    ass_plan=frappe.db.get_value("Assessment Plan",{"custom_institute_name":institute_name,"program":program,"academic_year":academic_year,"academic_term":academic_term,"docstatus":1},["name"])
    if ass_plan:
        ass_min_mark=frappe.db.get_value("Assessment Plan",{"name":ass_plan},["custom_minimum_score"])
        ass_result = frappe.db.sql(
            """
            SELECT student, program, academic_term
            FROM `tabAssessment Result`
            WHERE assessment_plan = %s AND docstatus = 1 AND total_score >= %s
            """,
            (ass_plan, ass_min_mark),
            as_dict=True
        )
        for i in ass_result:
            data.append([i.student,i.program,i.academic_term])
    else:
        frappe.msgprint("No assessment plan found for the provided criteria.")
    return data