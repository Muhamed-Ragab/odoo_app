{
    "name": "HMS",
    "version": "1.0",
    "category": "Hospital",
    "summary": "Hospitals Management System",
    "depends": ["base", "crm"],
    "data": [
        "security/ir.model.access.csv",
        "views/hms_patient_views.xml",
        "views/hms_department_views.xml",
        "views/hms_doctors_views.xml",
        "views/res_partner_views.xml",
    ],
    "author": "Mohamed",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "sequence": 1,
}
