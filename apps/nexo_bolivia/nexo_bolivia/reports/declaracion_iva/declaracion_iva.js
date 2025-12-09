// Copyright (c) 2024, Aero and contributors
// For license information, please see license.txt

frappe.query_reports["Declaración Jurada IVA"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12",
            "default": new Date().getMonth() + 1
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": new Date().getFullYear()
        }
    ],
    onload: function(report) {
        report.page.add_inner_button(__("Export to PDF"), function() {
            let filters = report.get_values();
            frappe.call({
                method: "nexo_bolivia.reports.declaracion_iva.declaracion_iva.export_form_200_pdf",
                args: {
                    company: filters.company,
                    month: filters.month,
                    year: filters.year
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__("Form 200 exported successfully"));
                    }
                }
            });
        });
    }
};
