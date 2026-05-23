// Copyright (c) 2024, Abdulla PI and contributors
// For license information, please see license.txt

frappe.provide("erpnext.accounts.dimensions");

frappe.ui.form.on("Fees Collection", {
	after_insert: function(frm){
		frappe.call({
			method: "hindustan.hindustan.doctype.fees_collection.fees_collection.get_rec_no",
			callback(r){
				if (r.message){
					frm.set_value("receipt_number",r.message)
				}
				else{
					frm.set_value("receipt_number",'')
				}
			}
		})
		frm.save()
		frm.reload_doc()
	},
	company: function(frm) {
		erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
	},
	before_cancel: function(frm) {
        if(!frm.doc.cancellation_remarks){
            frappe.validated = false;
            let d = new frappe.ui.Dialog({
                title: 'Provide Cancellation Remarks',
                fields: [
                    {
                        label: 'Cancellation Remarks',
                        fieldname: 'cancellation_remarks',
                        fieldtype: 'Small Text',
                        reqd: 1, 
                        allow_on_submit:1,
                    }
                ],
                primary_action_label: 'Cancel',
                primary_action(values) {
                    frm.set_value('cancellation_remarks', values.cancellation_remarks);
                    frm.save('Update')
                        .then(() => {
                            frappe.call({
                                method: 'frappe.client.cancel',
                                args: {
                                    doctype: frm.doc.doctype,
                                    name: frm.doc.name,
                                },
                                callback: function(r) {
                                    if (!r.exc) {
                                        frm.reload_doc();
                                    } 
                                },
                            });
                        })
        
                    d.hide();
                },
            });
        
            d.show();
            frm.reload_doc();
        }
    },
	onload: function(frm) {
		frm.set_query("concession_on", function() {
            return {
                query: "hindustan.custom.get_fees_category_options",
                filters: { fees: frm.doc.fees }
            };
        });
		if (!frm.doc.receipt_number){
			frappe.call({
				method: "hindustan.hindustan.doctype.fees_collection.fees_collection.get_rec_no",
				callback(r){
					if (r.message){
						frm.set_value("receipt_number",r.message)
					}
					else{
						frm.set_value("receipt_number",'')
					}
				}
			})
		}
		frm.set_query("academic_term", function() {
			return{
				"filters": {
					"academic_year": (frm.doc.academic_year) ,
					"program": frm.doc.program
				}
			};
		});
		frm.set_query("fee_structure", function() {
			return{
				"filters":{
					"academic_year": frm.doc.academic_year,
					"program": frm.doc.program,
					"academic_term": frm.doc.academic_term,
					"student_category" : frm.doc.custom_student_category,
					"docstatus": 1
				}
			};
		});
		frm.set_query("program_enrollment", function() {
			return{
				"filters":{
					"student": frm.doc.student,
					"academic_year": frm.doc.academic_year,
					"academic_term": frm.doc.academic_term,
					"docstatus": 1
				}
			};
		});
		frm.set_query("receivable_account", function(doc) {
			return {
				filters: {
					'account_type': 'Receivable',
					'is_group': 0,
					'company': doc.company
				}
			};
		});
		frm.set_query("income_account", function(doc) {
			return {
				filters: {
					'account_type': 'Income Account',
					'is_group': 0,
					'company': doc.company
				}
			};
		});
		if (!frm.doc.posting_date) {
			frm.doc.posting_date = frappe.datetime.get_today();
		}

		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},
	validate: function(frm) {
		if (!frm.doc.pay_advance){
			frm.set_value('excess_amount',0)
		}
		frm.trigger('calculate_paying_amount')
	},
	on_submit: function(frm) {
		frappe.run_serially([
			() => frappe.msgprint(__('Processing... Please wait')),
			() => new Promise(resolve => {
				frm.trigger('make_payment_entry');
				setTimeout(resolve, 3000);
			}),
			() => {
				// if (frm.doc.mark_concession && frm.doc.concession_on && frm.doc.concession_amount) {
					return frappe.call({
						method: "hindustan.hindustan.doctype.fees_collection.fees_collection.update_outstanding_amount",
						args: {
							fee_name: frm.doc.fees,
						}
					})
				// }
			},
			() => frappe.msgprint(__('Outstanding Amount updated Successfully')),
		]);

		
		
	},	
	
	refresh: function(frm) {
		frappe.breadcrumbs.add('Education', 'Fees Collection');
		if(frm.doc.docstatus == 0 && frm.doc.set_posting_time) {
			frm.set_df_property('posting_date', 'read_only', 0);
			frm.set_df_property('posting_time', 'read_only', 0);
		} else {
			frm.set_df_property('posting_date', 'read_only', 1);
			frm.set_df_property('posting_time', 'read_only', 1);
		}
		// if(frm.doc.docstatus > 0) {
		// 	frm.add_custom_button(__('Accounting Ledger'), function() {
		// 		frappe.route_options = {
		// 			voucher_no: frm.doc.name,
		// 			from_date: frm.doc.posting_date,
		// 			to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
		// 			company: frm.doc.company,
		// 			group_by: '',
		// 			show_cancelled_entries: frm.doc.docstatus === 2
		// 		};
		// 		frappe.set_route("query-report", "General Ledger");
		// 	}, __("View"));
		// 	frm.add_custom_button(__("Payments"), function() {
		// 		frappe.set_route("List", "Payment Entry", {"Payment Entry Reference.reference_name": frm.doc.name});
		// 	}, __("View"));
		// }
		// if(frm.doc.docstatus===1 && frm.doc.outstanding_amount>0) {
		// 	frm.add_custom_button(__("Payment Request"), function() {
		// 		frm.events.make_payment_request(frm);
		// 	}, __('Create'));
		// 	frm.page.set_inner_btn_group_as_primary(__('Create'));
		// }
		// if(frm.doc.docstatus===1 && frm.doc.outstanding_amount!=0) {
		// 	frm.add_custom_button(__("Payment"), function() {
		// 		frm.events.make_payment_entry(frm);
		// 	}, __('Create'));
		// 	frm.page.set_inner_btn_group_as_primary(__('Create'));
		// }
	},


	student: function(frm) {
		if (frm.doc.student) {
			frappe.db.get_value("Student", frm.doc.student, "custom_current_academic_term")
			.then((r) => {
				if (r.message) {
					frm.set_value("academic_term", r.message.custom_current_academic_term)
				}
			})
		}
		else{
			frm.set_value("program_enrollment", "");
			frm.set_value("program", "");
			frm.set_value("fee_structure", "");
		}
	},

	make_payment_request: function(frm) {
		if (!frm.doc.contact_email) {
			frappe.msgprint(__("Please set the Email ID for the Student to send the Payment Request"));
		} else {
			frappe.call({
				method:"erpnext.accounts.doctype.payment_request.payment_request.make_payment_request",
				args: {
					"dt": frm.doc.doctype,
					"dn": frm.doc.name,
					"party_type": "Student",
					"party": frm.doc.student,
					"recipient_id": frm.doc.contact_email
				},
				callback: function(r) {
					if(!r.exc){
						var doc = frappe.model.sync(r.message);
						frappe.set_route("Form", doc[0].doctype, doc[0].name);
					}
				}
			});
		}
	},

	make_payment_entry: function(frm) {
		return frappe.call({
			method: "hindustan.hindustan.doctype.fees_collection.fees_collection.get_payment_entry",
			args: {
				"dt": "Fees",
				"dn": frm.doc.fees,
				"party_type": "Student",
				"payment_type": "Receive",
				"allocated": frm.doc.paying_amount,
				"docname": frm.doc.name,
				"fc_type": "Fees Collection",
				"fc_name": frm.doc.name,
			},
			callback: function(r) {
				if (r.message) {
					frappe.model.sync(r.message);
					frappe.db.insert(r.message).then((doc) => {
						frappe.msgprint(__("Payment Entry <b>{0}</b> created successfully.", [doc.name]));
						frappe.call({
							method: "frappe.client.submit",
							args: {
								doc: doc, 
							},
						});
						
					}).catch((error) => {
						frappe.msgprint(__("Failed to create Payment Entry: {0}", [error.message]));
					});
				} else {
					frappe.msgprint(__("No Payment Entry was created."));
				}
			}
		});
	},
	

	set_posting_time: function(frm) {
		frm.refresh();
	},

	academic_term: function() {
		frappe.ui.form.trigger("Fees Collection", "program");
		// if (frm.doc.program && frm.doc.academic_term && frm.doc.academic_year) {
        // 	frm.trigger('get_program_enrollment');
		// }
	},

	fees: function(frm) {
		frm.set_value("components" ,"");
		if (frm.doc.fee_structure) {
			frappe.call({
				method: "hindustan.hindustan.doctype.fees_collection.fees_collection.get_fee_components",
				args: {
					"fee_structure": frm.doc.fees
				},
				callback: function(r) {
					if (r.message) {
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(frm.doc, "Fee Collection Component", "components");
							row.fees_category = d.fees_category;
							row.description = d.description;
							row.amount = d.amount;
							row.amount_paid = d.custom_amount_paid
							row.outstanding_amount = d.custom_outstanding_amount
						});
					}
					refresh_field("components");
					frm.trigger("calculate_total_amount");
				}
			});
		}
	},

	calculate_total_amount: function(frm) {
		var grand_total = 0;
		var amount_paid = 0;
		var outstanding_amount = 0;
		for(var i=0;i<frm.doc.components.length;i++) {
			grand_total += frm.doc.components[i].amount;
			amount_paid += frm.doc.components[i].amount_paid;
			outstanding_amount += frm.doc.components[i].outstanding_amount;
		}
		frm.set_value("grand_total", grand_total);
		frm.set_value("amount_paid", amount_paid);
		frm.set_value("outstanding_amount", outstanding_amount);
	},

	calculate_paying_amount: function(frm) {
        var paying_amount = 0;
        (frm.doc.components || []).forEach(component => {
            paying_amount += component.paying_amount || 0;
        });
        frm.set_value("paying_amount", paying_amount);
    },
	
	program(frm) {
		if (frm.doc.program && frm.doc.academic_term && frm.doc.academic_year) {
        	frm.trigger('get_program_enrollment');
		}
    },

	get_advance: function (frm) {
		if (frm.doc.get_advance == 1) {
			frm.set_df_property('advance_payment', 'hidden', 0);
			frappe.db.get_value('Advance Fees', { registration_number: frm.doc.registration_number }, 'name')
				.then(response => {
					const advance_fees_name = response.message.name;
					
					if (advance_fees_name) {
						frappe.db.get_doc('Advance Fees', advance_fees_name)
							.then(advance_fees => {
								if (advance_fees && advance_fees.advance_payment) {
									frm.clear_table('advance_payment');
									advance_fees.advance_payment.forEach(row => {
										if (!row.adjusted) {
											let new_row = frm.add_child('advance_payment');
											new_row.reference_type = row.reference_type;
											new_row.reference_number = row.reference_number;
											new_row.date = row.date;
											new_row.adjusted = row.adjusted;
											new_row.received_amount = row.balance_amount;
											new_row.balance_amount = row.balance_amount
										}
									});
	
									frm.refresh_field('advance_payment');
								} else {
									frappe.msgprint(__('No Advance Payment data found in the selected Advance Fees document.'));
								}
							})
					} else {
						frappe.msgprint(__('No Advance Fees document found for the given registration number.'));
					}
				});
		} else {
			frm.clear_table('advance_payment');
			frm.refresh_field('advance_payment');
			
			frm.set_df_property('advance_payment', 'hidden', 1);
		}
		setTimeout(function() {
			frm.save();
		}, 500);
	},
	// adjust_advance: function(frm) {
	// 	if (!frm.doc.advance_payment || !frm.doc.components) {
	// 		frappe.msgprint(__('Advance Payment or Components table is missing.'));
	// 		return;
	// 	}
	
	// 	if (frm.doc.advance_payment.length > 0) {
	// 		let rec_amt = 0;
	// 		let adj_amt = 0;
	
	// 		frm.doc.advance_payment.forEach(row => {
	// 			rec_amt += row.received_amount || 0;
	// 		});
	
	// 		frm.doc.components.forEach(child => {
	// 			if (child.outstanding_amount > 0) {
	// 				if (rec_amt >= child.outstanding_amount) {
	// 					child.paying_amount = child.outstanding_amount;
	// 					rec_amt -= child.outstanding_amount;
	// 				} else {
	// 					child.paying_amount = rec_amt;
	// 					rec_amt = 0;
	// 				}
	// 				adj_amt += child.paying_amount || 0;
	// 			}
	// 		});
	
	// 		let total_received = frm.doc.advance_payment.reduce((sum, row) => sum + (row.received_amount || 0), 0);
	// 		frm.doc.advance_payment.forEach(row => {
	// 			row.adjusted_amount = total_received ? (row.received_amount / total_received) * adj_amt : 0;
	// 			row.adjusted = row.received_amount === row.adjusted_amount;
				
	// 		});
	
	// 		frm.refresh_field('components');
	// 		frm.refresh_field('advance_payment');
	// 	}
	// },

	adjust_advance: function(frm) {
		if (!frm.doc.advance_payment || !frm.doc.components) {
			frappe.msgprint(__('Advance Payment or Components table is missing.'));
			return;
		}

		if (frm.doc.advance_payment.length > 0) {
			let rec_amt = 0;
			let adj_amt = 0;

			// Step 1: Calculate Total Advance Amount Available
			frm.doc.advance_payment.forEach(row => {
				rec_amt += row.received_amount || 0;
			});

			// Step 2: Clear previous paying_amount
			(frm.doc.components || []).forEach(child => {
				child.paying_amount = 0;
			});

			// Step 3: Adjust against Fee Components
			(frm.doc.components || []).forEach(child => {
				if (child.outstanding_amount > 0) {
					if (rec_amt >= child.outstanding_amount) {
						child.paying_amount = child.outstanding_amount;
						rec_amt -= child.outstanding_amount;
					} else {
						child.paying_amount = rec_amt;
						rec_amt = 0;
					}
					adj_amt += child.paying_amount || 0;
				}
			});

			// Step 4: Allocate Adjusted Amount across Advance rows proportionally
			let total_received = frm.doc.advance_payment.reduce((sum, row) => sum + (row.balance_amount || 0), 0);

			frm.doc.advance_payment.forEach(row => {
				let share_ratio = row.balance_amount / total_received;
				let adjusted_amt = share_ratio * adj_amt;

				row.adjusted_amount = adjusted_amt;
				row.received_amount=row.balance_amount;
				row.balance_amount = row.received_amount - adjusted_amt;
				row.adjusted = row.balance_amount <= 0.001;  // true if fully adjusted
				
			});

			// Refresh fields
			frm.refresh_field('advance_payment');
			frm.refresh_field('components');
		}
},

	
	concession_amount(frm) {
		frm.save();
	},
	
	academic_year(frm) {
		if (frm.doc.program && frm.doc.academic_term && frm.doc.academic_year) {
        	frm.trigger('get_program_enrollment');
		}
    },
	admission_number(frm){
		if(frm.doc.admission_number){
			frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Student",
                    filters: {
                        custom_admission_number: frm.doc.admission_number
                    },
                    fieldname: "name"
                },
				
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("student", r.message.name);
                    } 
                }
            });
		}
		
	},
    get_program_enrollment: function(frm) {
        
            frappe.db.get_value('Fees',
				{program: frm.doc.program,academic_term: frm.doc.academic_term,academic_year: frm.doc.academic_year, student:frm.doc.student, "docstatus": 1},
				['fee_structure', 'due_date', 'fee_schedule', 'program_enrollment', 'student_batch', 'student_category', 'name'])
            .then(r => {
                if (r.message) {
                    frm.set_value('fee_structure', r.message.fee_structure);
					frm.set_value('due_date', r.message.due_date);
					frm.set_value('fee_schedule', r.message.fee_schedule);
					frm.set_value('program_enrollment', r.message.program_enrollment);
					frm.set_value('student_batch', r.message.student_batch);
					frm.set_value('student_category', r.message.student_category);
					frm.set_value('fees', r.message.name);
                } else {
                    frappe.msgprint(__('OOOPS'));
                }
            });
    }
});


frappe.ui.form.on("Fee Collection Component", {
	amount: function(frm) {
		frm.trigger("calculate_total_amount");
	},
	paying_amount: function(frm) {
		frm.trigger("calculate_paying_amount")
	},
});

