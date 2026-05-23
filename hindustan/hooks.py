app_name = "hindustan"
app_title = "Hindustan"
app_publisher = "Abdulla PI"
app_description = "Education Module App"
app_email = "abdulla.pi@groupteampro.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "hindustan",
# 		"logo": "/assets/hindustan/logo.png",
# 		"title": "Hindustan",
# 		"route": "/hindustan",
# 		"has_permission": "hindustan.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hindustan/css/hindustan.css"
# app_include_js = "/assets/hindustan/js/hindustan.js"

# include js, css files in header of web template
# web_include_css = "/assets/hindustan/css/hindustan.css"
# web_include_js = "/assets/hindustan/js/hindustan.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hindustan/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hindustan/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    "methods":[
        "hindustan.hindustan.doctype.report_dashboard.consolidated_salary_statement.print_consolidated_salary",
        "hindustan.salary_slip_custom.format_currency",
        "hindustan.admission_custom.add_suffix_to_date",
        "hindustan.hindustan.doctype.report_dashboard.salary_register.get_salary_register_data_for_jinja",
        "hindustan.hindustan.doctype.report_dashboard.consolidated_report.get_consolidated_statement_data_for_jinja",
    ]
	# "methods": "hindustan.utils.jinja_methods",
# 	"filters": "hindustan.utils.jinja_filters"
}

# Installation
# ------------

# before_install = "hindustan.install.before_install"
# after_install = "hindustan.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hindustan.uninstall.before_uninstall"
# after_uninstall = "hindustan.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hindustan.utils.before_app_install"
# after_app_install = "hindustan.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hindustan.utils.before_app_uninstall"
# after_app_uninstall = "hindustan.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hindustan.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
    "Employee": {
        "after_insert": [
            "hindustan.employee_custom.teaching_type"  
        ],
        "on_update": [
            "hindustan.employee_custom.teaching_type"  
        ],
        "validate":[
            "hindustan.employee_custom.employee_doc_validation_method"
        ]
    },
    "Fee Structure":{
        "on_submit":'hindustan.fee_str_custom.create_update_overall_fee_structure',
		"on_cancel":'hindustan.fee_str_custom.create_update_overall_fee_structure'
  	},
    "Payment Entry": {
        "on_submit": "hindustan.payment_entry_custom.create_student_log_on_payment",
        "on_cancel": "hindustan.payment_entry_custom.delete_student_log_on_payment"
    },
    "Fees": {
        "validate": [
            "hindustan.fees_custom.validate_advance_payments",
            "hindustan.fees_custom.validate_outstanding_amount",
            # "hindustan.custom.program_change_check",
        ],
        "on_update_after_submit":[
            "hindustan.fees_custom.validate_advance_payments",
            "hindustan.fees_custom.validate_outstanding_amount",
            # "hindustan.custom.program_change_check",
        ],
        "before_insert":"hindustan.fees_custom.program_change_check",
        # "on_submit": ["hindustan.custom.create_fees_collection_for_registration"]
    },
	"Leave Application":{
		"validate": ['hindustan.leave_app_custom.leave_restriction_el_after','hindustan.leave_app_custom.leave_restriction_el_before','hindustan.leave_app_custom.leave_restriction_combining_after','hindustan.leave_app_custom.leave_restriction_combining_before'],
	},
    "Admission":{
        "before_cancel": "hindustan.admission_custom.cancellation_remarks_mandatory"
    },
    "Salary Slip":{
        "after_insert": "hindustan.salary_slip_custom.update_earned_basic"
    },
    "Student":{
        "validate":["hindustan.stud_custom.student_doc_validation_method","hindustan.stud_custom.validate_mail",
                    # "hindustan.custom.create_enrollment_test"
                    ],
        'after_insert':["hindustan.stud_custom.create_enrollment","hindustan.stud_custom.update_student_number",'hindustan.stud_custom.update_receiving_person']
    },
    "Receiving Person": {
        "after_insert": "hindustan.receiving_person_custom.rename_receiver"
    },
    'Academic Term':{
        "validate": "hindustan.acad_term_custom.check_academic_term"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hindustan.tasks.all"
# 	],
# 	"daily": [
# 		"hindustan.tasks.daily"
# 	],
# 	"hourly": [
# 		"hindustan.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hindustan.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hindustan.tasks.monthly"
# 	],
# }
# hooks.py

scheduler_events = {
    "cron": {
        "*/2 * * * *": [
            "hindustan.leave_all_custom.allocate_leaves_automatically"
        ]
    }
}
# Testing
# -------
override_doctype_class = {
    "Fee Schedule":"hindustan.overrides.CustomFeeSchedule",
    "Salary Slip":"hindustan.overrides.CustomSalarySlip",

}

# before_tests = "hindustan.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hindustan.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hindustan.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hindustan.utils.before_request"]
# after_request = ["hindustan.utils.after_request"]

# Job Events
# ----------
# before_job = ["hindustan.utils.before_job"]
# after_job = ["hindustan.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hindustan.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

