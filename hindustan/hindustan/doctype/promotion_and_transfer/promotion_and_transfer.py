# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hindustan.hindustan.doctype.admission.admission import get_adm_no
from hindustan.hindustan.doctype.registration.registration import get_reg_no
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
                    create_enrollment(self.student_id__admission_id)
            if self.student_promotion and not self.student_id__admission_id:
                for i in self.student_promotion:
                    if not self.promotion_academic_year:
                        frappe.throw("Promotion Academic Year is required")
                    elif not self.promotion_sem__batch:
                        frappe.throw("Promotion Sem / Batch is required")
                    # if self.student_promotion and self.promotion_sem__batch:
                    #     student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                    #     student.custom_promoted_academic_year=self.promotion_academic_year
                    #     student.custom_current_academic_term=self.promotion_sem__batch
                    #     student.save()
                    #     frappe.db.commit()
                    #     create_enrollment(i.student_id__admission_id)
                    if self.student_promotion and self.promotion_sem__batch:
                        for i in self.student_promotion:   
                            if not i.student_id__admission_id:
                                continue
                            student = frappe.get_doc("Student", i.student_id__admission_id)
                            student.custom_promoted_academic_year = self.promotion_academic_year
                            student.custom_current_academic_term = self.promotion_sem__batch
                            student.save(ignore_permissions=True)
                            create_enrollment(student.name)
        elif self.transfer==1:
            if self.student_id__admission_id and not self.student_promotion:
                student_id=[self.student_id__admission_id]
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
                    if self.transfered_student_category:
                        student.custom_student_category=self.transfered_student_category
                    if self.student_category:
                        student.custom_transfered_student_category=self.student_category
                    student.save()
                    frappe.db.commit()
                    create_enrollment(self.student_id__admission_id)
                    if self.institute_name!=self.transfered_institute_name:
                        adm=frappe.db.get_value('Student',{'name':self.student_id__admission_id},['custom_admission_number'])
                        updated_adm=get_adm_no(self.transfered_institute_name,adm)
                        frappe.rename_doc('Admission',adm,updated_adm)
                        frappe.db.set_value('Admission',updated_adm,"institution_name",self.transfered_institute_name)
                        reg=frappe.db.get_value('Student',{'name':self.student_id__admission_id},['custom_registration_number'])
                        updated_reg=get_reg_no(self.transfered_institute_name,reg)
                        frappe.rename_doc('Registration',reg,updated_reg)
                        frappe.db.set_value('Registration',updated_reg,"institution_name",self.transfered_institute_name)

                    
            if self.student_promotion and not self.student_id__admission_id:
                student_id=[]
                for i in self.student_promotion:
                    if not self.transfered_academic_year:
                        frappe.throw("PromotionAndTransfer Academic Year is required")
                    elif not self.transfered_sembatch:
                        frappe.throw("PromotionAndTransfer Sem / Batch is required")
                    if self.student_promotion and self.transfered_sembatch:
                        student_id.append(i.student_id__admission_id)
                        student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
                        student.custom_transfered_academic_year=self.transfered_academic_year
                        student.custom_transfered_academic_term=self.transfered_sembatch
                        student.custom_transfered_institute=self.transfered_institute_name
                        student.custom_transfered_program=self.transfered_program
                        student.custom_academic_year=self.transfered_academic_year
                        student.custom_program=self.transfered_program
                        student.custom_current_academic_term=self.transfered_sembatch
                        student.custom_institute_name=self.transfered_institute_name
                        if self.transfered_student_category:
                            student.custom_student_category=self.transfered_student_category
                        if self.student_category:
                            student.custom_transfered_student_category=self.student_category
                        student.save(ignore_permissions=True)
                        frappe.db.commit()
            for s in student_id:
                student_doc=frappe.get_doc("Student",{'name':s}) 
                concession=frappe.db.get_all("Concession",{'student':student_doc.name},['name'])
                if concession:
                    for c in concession:
                        conc=frappe.get_doc("Concession",c.name)
                        if conc.docstatus==1:
                            conc.cancel()
                            # conc.delete(ignore_permissions=True)
                            frappe.db.commit()
                        # else:
                        #     conc.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                fee_coll=frappe.db.get_all("Fees Collection",{'student':student_doc.name},['name'])
                if fee_coll:
                    for feec in fee_coll:
                        fc=frappe.get_doc("Fees Collection",feec.name)
                        if fc.docstatus==1:
                            fc.cancel()
                            # fc.delete(ignore_permissions=True)
                            frappe.db.commit()
                        # else:
                        #     fc.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                advfee=frappe.db.get_all("Advance Fees",{'student':student_doc.name},['name'])
                if advfee:
                    for ad in advfee:
                        adv=frappe.get_doc("Advance Fees",ad.name)
                        if adv.docstatus==1:
                            adv.cancel()
                            # adv.delete(ignore_permissions=True)
                            frappe.db.commit()
                        # else:
                        #     adv.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                additional=frappe.db.get_all("Additional Fee",{'student':student_doc.name},['name'])
                if additional:
                    for add in additional:
                        add_fee=frappe.get_doc("Additional Fee",add.name)
                        if add_fee.docstatus==1:
                            add_fee.cancel()
                            # add_fee.delete(ignore_permissions=True)
                            frappe.db.commit()
                        # else:
                        #     add_fee.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                fee_doc=frappe.db.get_all("Fees",{'student':student_doc.name},['name'])
                if fee_doc:
                    for f in fee_doc:
                        fees=frappe.get_doc("Fees",f.name)
                        if fees.docstatus==1:
                            fees.cancel()
                            frappe.db.commit()
                        # glentry=frappe.db.get_all("GL Entry",{'party':student_doc.name,'voucher_type':'Payment Entry'},['name'])
                        # for gl_ent in glentry:
                        #     gl_entry=frappe.get_doc("GL Entry",gl_ent.name)
                        #     gl_entry.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                        # glentryy=frappe.db.get_all("GL Entry",{'against':student_doc.name,'voucher_type':'Payment Entry'},['name'])
                        # for gl_entr in glentryy:
                        #     gl_entry=frappe.get_doc("GL Entry",gl_entr.name)
                        #     gl_entry.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                        # payentry=frappe.db.get_all("Payment Entry",{'party':student_doc.name},['name'])
                        # if payentry:
                        #     for p in payentry:
                        #         if frappe.db.exists("Payment Ledger Entry",{'voucher_no':p.name}):
                        #             pledger=frappe.db.get_all("Payment Ledger Entry",{'voucher_no':p.name},['name'])
                        #             for plentry in pledger:
                        #                 pay_ledger=frappe.get_doc("Payment Ledger Entry",plentry)
                        #                 pay_ledger.delete(ignore_permissions=True)
                        #                 frappe.db.commit()
                        #         if frappe.db.exists("Payment Entry Reference",{'reference_name':f.name,'parent':p.name}):
                        #             pe=frappe.get_doc("Payment Entry",p.name)
                        #             if pe.docstatus==1:
                        #                 pe.cancel()
                        #                 pe.delete(ignore_permissions=True)
                        #                 frappe.db.commit()
                        #             else:
                        #                 pe.delete(ignore_permissions=True)
                        #                 frappe.db.commit()

                        # gl_pe=frappe.db.get_all("GL Entry",{'against':student_doc.name,'voucher_type':'Payment Entry'},['name'])
                        # for gp in gl_pe:
                        #     gle=frappe.get_doc("GL Entry",gp.name)
                        #     gle.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                        # gl_vno=frappe.db.get_all("GL Entry",{'voucher_no':f},['name'])
                        # for glv in gl_vno:
                        #     gl_vo=frappe.get_doc("GL Entry",glv.name)
                        #     gl_vo.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                        # pl=frappe.db.get_all("Payment Ledger Entry",{'voucher_no':f},['name'])
                        # for gpl in pl:
                        #     ple=frappe.get_doc("Payment Ledger Entry",gpl.name)
                        #     ple.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                        # pl=frappe.db.get_all("Payment Ledger Entry",{'against_voucher_no':f},['name'])
                        # for gpl in pl:
                        #     ple=frappe.get_doc("Payment Ledger Entry",gpl.name)
                        #     ple.delete(ignore_permissions=True)
                        #     frappe.db.commit()
                        # fees.delete(ignore_permissions=True)
                        # frappe.db.commit()
                student_group=frappe.db.get_all("Student Group",['name'])
                for st in student_group:
                    sg=frappe.get_doc('Student Group',st.name)
                    for stu in sg.students:
                        if stu.student==student_doc.name:
                            sg.remove(stu)  
                            break 
                    sg.save(ignore_permissions=True)
                    frappe.db.commit()
                    sg.reload()
                    count=1
                    for stu in sg.students:
                        stu.group_roll_number=count
                        count+=1
                    sg.save(ignore_permissions=True)
                    frappe.db.commit()
                prog_enroll=frappe.db.get_all("Program Enrollment",{'student':student_doc.name},['name'])
                if prog_enroll:
                    for prog in prog_enroll:
                        pro=frappe.get_doc("Program Enrollment",prog)
                        if pro.docstatus==1:
                            pro.cancel()
                        # pro.delete(ignore_permissions=True)
                        frappe.db.commit()
                create_enrollment(student_doc.name)
                if self.institute_name!=self.transfered_institute_name:
                    adm=frappe.db.get_value('Student',{'name':student_doc.name},['custom_admission_number'])
                    updated_adm=get_adm_no(self.transfered_institute_name,adm)
                    frappe.rename_doc('Admission',adm,updated_adm)
                    reg=frappe.db.get_value('Student',{'name':student_doc.name},['custom_registration_number'])
                    updated_reg=get_reg_no(self.transfered_institute_name,reg)
                    frappe.rename_doc('Registration',reg,updated_reg)
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
        # create_enrollment(student_doc.name)
    # def on_cancel(self):
    #     if self.promotion__transfer==1:
    #         if self.student_id__admission_id and not self.student_promotion:
    #             student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
    #             student.custom_promoted_academic_year=self.academic_year
    #             student.custom_current_academic_term=self.batchsem
    #             student.save()
    #             frappe.db.commit()
    #         if self.student_promotion and not self.student_id__admission_id:
    #             for i in self.student_promotion:
    #                 student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
    #                 student.custom_promoted_academic_year=self.academic_year
    #                 student.custom_current_academic_term=self.batchsem
    #                 student.save()
    #                 frappe.db.commit()
    #     elif self.transfer==1:
    #         if self.student_id__admission_id and not self.student_promotion:
    #             if self.transfered_academic_year and self.transfered_sembatch:
    #                 student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
    #                 student=frappe.get_doc("Student",{"name":self.student_id__admission_id})
    #                 student.custom_academic_year=self.academic_year
    #                 student.custom_program=self.program
    #                 student.custom_current_academic_term=self.batchsem
    #                 student.custom_institute_name=self.institute_name
    #                 student.custom_transfered_academic_year=""
    #                 student.custom_transfered_academic_term=""
    #                 student.custom_transfered_institute=""
    #                 student.custom_transfered_program=""
    #                 student.save()
    #                 frappe.db.commit()
    #         if self.student_promotion and not self.student_id__admission_id:
    #             for i in self.student_promotion:
    #                 if self.student_promotion and self.transfered_sembatch:
    #                     student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
    #                     student.custom_transfered_academic_year=""
    #                     student.custom_transfered_academic_term=""
    #                     student.custom_transfered_institute=""
    #                     student.custom_transfered_program=""
    #                     student.save()
    #                     frappe.db.commit()
    #     elif self.promotion_and_transfer_via_assessment==1:
    #         if self.student_promotion:
    #             for i in self.student_promotion:
    #                 student=frappe.get_doc("Student",{"name":i.student_id__admission_id})
    #                 student.custom_promoted_academic_year=self.academic_year
    #                 student.custom_current_academic_term=self.batchsem
    #                 student.save()
    #                 frappe.db.commit()



@frappe.whitelist()
def get_student_details(inst_name,program,sem,year):
    data=[]
    students=frappe.db.get_all("Student",{"custom_academic_year":year,"custom_program":program,"custom_institute_name":inst_name,"custom_current_academic_term":sem,"enabled":1},["*"])
    if students:
        for i in students:
            data.append([i.name,i.custom_program,i.custom_current_academic_term])
    else:
        frappe.msgprint("No Students found")
    return data


@frappe.whitelist()
def get_student_details_for_transfer(inst_name,program,sem,year,student_category):
    data=[]
    students=frappe.db.get_all("Student",{"custom_academic_year":year,"custom_program":program,"custom_institute_name":inst_name,"custom_current_academic_term":sem,"custom_student_category":student_category,"enabled":1},["*"])
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



@frappe.whitelist()
def create_enrollment(student):
    doc=frappe.get_doc('Student',student)
    sem=frappe.db.get_all("Academic Term",{'academic_year':doc.custom_academic_year,'program':doc.custom_program},['name'])
    for s in sem:
        if not frappe.db.exists("Program Enrollment",{'student':doc.name,'academic_year':doc.custom_academic_year,'academic_term':s.name,'program':doc.custom_program,'docstatus':1}):
            edate=frappe.db.get_value("Academic Term",{'name':s.name},['term_start_date'])
            enroll=frappe.new_doc("Program Enrollment")
            enroll.student=doc.name
            enroll.program=doc.custom_program
            enroll.academic_year=doc.custom_academic_year
            enroll.enrollment_date=edate
            enroll.academic_term=s.name
            enroll.student_category=doc.custom_student_category
            if not frappe.db.exists("Student Batch Name",{'batch_name':doc.custom_academic_year}):
                batch=frappe.new_doc('Student Batch Name')
                batch.batch_name=doc.custom_academic_year
                # batch.insert(ignore_permissions=True)
                batch.save(ignore_permissions=True)
                frappe.db.commit()
                batch=batch.name
            else:
                batch=frappe.db.get_value("Student Batch Name",{'batch_name':doc.custom_academic_year},['name'])
            enroll.student_batch_name=batch
            # enroll.insert(ignore_permissions=True)
            enroll.save(ignore_permissions=True)
            enroll.submit()
            frappe.db.commit()
            if not frappe.db.exists("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
                                              "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category}):
                new = frappe.new_doc("Student Group")
                new.academic_year = enroll.academic_year
                new.group_based_on = "Batch"
                sem_no=frappe.db.get_value("Academic Term",{'name':enroll.academic_term},['custom_semester'])
                new.student_group_name = enroll.academic_term + "-" + enroll.program + "-" + sem_no + "-" +enroll.student_category
                new.academic_term =enroll.academic_term
                new.program = enroll.program
                new.batch = enroll.student_batch_name
                new.student_category = enroll.student_category
                new.max_strength = 0
                
                new.append('students', {
                            "student": enroll.student,
                        })
                new.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                std_group = frappe.get_doc("Student Group", {"academic_year": enroll.academic_year, "academic_term": enroll.academic_term, 
                                                    "program": enroll.program, "batch": enroll.student_batch_name, "student_category": enroll.student_category})
                std_group.append('students', {
                            "student": enroll.student,
                        })
                std_group.save(ignore_permissions=True)
                frappe.db.commit()




