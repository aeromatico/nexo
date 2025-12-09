// Copyright (c) 2024, Aero and contributors
// For license information, please see license.txt

frappe.query_reports["Libro de Ventas IVA"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.nowdate(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.nowdate()
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        }
    ],
    onload: function(report) {
        report.page.add_inner_button(__("Export to Excel"), function() {
            let filters = report.get_values();
            frappe.call({
                method: "nexo_bolivia.reports.libro_ventas_iva.libro_ventas_iva.export_to_excel",
                args: {filters: filters},
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__("File exported successfully"));
                    }
                }
            });
        });

        report.page.add_inner_button(__("Export to TXT"), function() {
            let filters = report.get_values();
            frappe.call({
                method: "nexo_bolivia.reports.libro_ventas_iva.libro_ventas_iva.export_to_txt",
                args: {filters: filters},
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__("File exported successfully"));
                    }
                }
            });
        });
    }
};
