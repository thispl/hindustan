# Copyright (c) 2024, Abdulla PI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OverallFeeStructure(Document):
	pass

@frappe.whitelist()
def get_fees_structure_html(program,name,no_of_semesters):
	no_of_semesters = int(no_of_semesters)
	data = """
			<h4 class='text-center' style="color: black;">Fee Structure</h4>
			<div style="overflow-x: auto; color: black;">
			<table width='100%' class="text-center">
			<thead>
			<tr style="background-color: #ffe5b4; font-weight: 500; color: black;">
			<th width="10%" class="border border-1 border-dark">No.</th>
			<th width="40%" class="border border-1 border-dark"">Fees Category</th>
		   """
	sem = []
	width = (50/no_of_semesters, 0)
	frappe.errprint(width)
	for idx in range(1, no_of_semesters + 1):
		data += f"""
					<th width="{width}%" class="border border-1 border-dark">Sem {idx}</th>
				"""
		sem.append({
			f"sem{idx}": 0
		})
	data += """
				</tr>
				</thead>
				<div>
			"""
	doc = frappe.get_doc("Overall Fee Structure", name)
	idx_row = 0
	grand_total = 0
	for row in doc.fee_structure:
		idx_row += 1
		# To make the total row bold
		if row.fees_category == "Total": 
			data += f"""
						<tr style="font-weight: 700">
						<td rowspan=2 class="border border-1 border-dark" style="text-align: center; font-weight: normal;">{idx_row}</td>
						<td rowspan=2 class="border border-1 border-dark" style="text-align: left; padding-left: 10px; padding-right: 5px;">{row.fees_category}</td>
					"""
			for i in range(1, no_of_semesters + 1):
				value = getattr(row, f"sem_{i}", 0)
				data += f"""
					<td class="border border-1 border-dark" style="text-align: right; padding-right: 10px;">
					&#x20b9 {format_currency(value)}</td>
				"""
				grand_total += value
			data += f"""
   						</tr>
						<tr><td colspan={no_of_semesters} class="border border-1 border-dark" style="text-align: center; font-weight: 700">
						&#x20b9 {format_currency(grand_total)}</td></tr>
         			"""
		#  Not bold
		else:
			data += f"""
						<tr>
						<td class="border border-1 border-dark" style="text-align: center">{idx_row}</td>
						<td class="border border-1 border-dark" style="text-align: left; padding-left: 10px; padding-right: 5px;">{row.fees_category}</td>
					"""
			for i in range(1, no_of_semesters + 1):
				value = getattr(row, f"sem_{i}", 0)
				data += f"""
					<td class="border border-1 border-dark" style="text-align: right; padding-right: 10px;">
					&#x20b9 {format_currency(value)}</td>
				"""
			data += "</tr>"
	return data

@frappe.whitelist()
def format_currency(value):
	if value is None:
		return "0"
	
	number_str = str(int(value))
	
	if len(number_str) > 3:
		last_three = number_str[-3:]  
		other_digits = number_str[:-3] 
		
		formatted_other = []
		while len(other_digits) > 2:
			formatted_other.append(other_digits[-2:])
			other_digits = other_digits[:-2]
		if other_digits:
			formatted_other.append(other_digits)        
		formatted_other.reverse()
		formatted_number = ','.join(formatted_other) + ',' + last_three
	else:
		formatted_number = number_str
	
	return formatted_number