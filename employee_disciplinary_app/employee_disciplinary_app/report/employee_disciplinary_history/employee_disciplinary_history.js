// Copyright (c) 2024, [Your Company] and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Disciplinary History"] = {
    "filters": [
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 100
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 100
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        },
        {
            "fieldname": "severity",
            "label": __("Severity"),
            "fieldtype": "Select",
            "options": "\nMinor\nModerate\nMajor\nCritical",
            "width": 100
        },
        {
            "fieldname": "risk_level",
            "label": __("Risk Level"),
            "fieldtype": "Select",
            "options": "\n🔴 Critical Risk\n🟠 High Risk\n🟡 Moderate Risk\n🟢 Low Risk\n⚪ Minimal Risk",
            "width": 100
        },
        {
            "fieldname": "min_incidents",
            "label": __("Minimum Incidents"),
            "fieldtype": "Int",
            "default": 1,
            "width": 100
        },
        {
            "fieldname": "include_terminated",
            "label": __("Include Terminated Employees"),
            "fieldtype": "Check",
            "default": 0
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color code risk levels
        if (column.fieldname == "risk_level") {
            if (value && value.includes("Critical")) {
                value = "<span style='color: #dc3545; font-weight: bold;'>" + value + "</span>";
            } else if (value && value.includes("High")) {
                value = "<span style='color: #fd7e14; font-weight: bold;'>" + value + "</span>";
            } else if (value && value.includes("Moderate")) {
                value = "<span style='color: #ffc107; font-weight: bold;'>" + value + "</span>";
            } else if (value && value.includes("Low")) {
                value = "<span style='color: #28a745;'>" + value + "</span>";
            }
        }
        
        // Color code total points
        if (column.fieldname == "total_points" && data) {
            if (data.total_points >= 20) {
                value = "<span style='color: #dc3545; font-weight: bold;'>" + value + "</span>";
            } else if (data.total_points >= 15) {
                value = "<span style='color: #fd7e14; font-weight: bold;'>" + value + "</span>";
            } else if (data.total_points >= 10) {
                value = "<span style='color: #ffc107;'>" + value + "</span>";
            }
        }
        
        // Highlight critical/major counts
        if ((column.fieldname == "critical_count" || column.fieldname == "major_count") && data) {
            if (parseInt(value) > 0) {
                value = "<span style='color: #dc3545; font-weight: bold;'>" + value + "</span>";
            }
        }
        
        // Highlight repeats
        if ((column.fieldname == "repeats_30" || column.fieldname == "repeats_90") && data) {
            if (parseInt(value) > 0) {
                value = "<span style='color: #fd7e14; font-weight: bold;'>" + value + "</span>";
            }
        }
        
        // Highlight recent incidents (within 30 days)
        if (column.fieldname == "days_since_last" && data) {
            if (data.days_since_last <= 30) {
                value = "<span style='color: #dc3545; font-weight: bold;'>" + value + "</span>";
            } else if (data.days_since_last <= 90) {
                value = "<span style='color: #ffc107;'>" + value + "</span>";
            } else if (data.days_since_last > 180) {
                value = "<span style='color: #28a745;'>" + value + "</span>";
            }
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add custom buttons
        report.page.add_inner_button(__("Export Detail View"), function() {
            export_detailed_report(report);
        });
        
        report.page.add_inner_button(__("Send Email Alerts"), function() {
            send_risk_alerts(report);
        }, __("Actions"));
        
        report.page.add_inner_button(__("View Individual History"), function() {
            view_individual_history(report);
        }, __("Actions"));
    }
};

// Export detailed view with all incidents per employee
function export_detailed_report(report) {
    frappe.call({
        method: "frappe.desk.query_report.export_query",
        args: {
            report_name: report.report_name,
            file_format_type: "Excel",
            filters: report.get_values(),
            visible_idx: report.visible_columns.map(col => col.fieldname)
        },
        callback: function(r) {
            if (r.message) {
                window.open(frappe.urllib.get_full_url(r.message));
            }
        }
    });
}

// Send email alerts for high-risk employees
function send_risk_alerts(report) {
    let data = report.data;
    let high_risk_employees = data.filter(emp => 
        emp.risk_level && (emp.risk_level.includes("Critical") || emp.risk_level.includes("High"))
    );
    
    if (high_risk_employees.length === 0) {
        frappe.msgprint(__("No high-risk employees found"));
        return;
    }
    
    frappe.confirm(
        __("Send email alerts for {0} high-risk employees?", [high_risk_employees.length]),
        function() {
            frappe.call({
                method: "your_app.hr.report.employee_disciplinary_history.employee_disciplinary_history.send_risk_alerts",
                args: {
                    employees: high_risk_employees.map(e => e.employee)
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__("Alerts sent successfully"));
                    }
                }
            });
        }
    );
}

// View individual employee's complete disciplinary history
function view_individual_history(report) {
    let selected_rows = report.get_checked_items();
    
    if (selected_rows.length === 0) {
        frappe.msgprint(__("Please select at least one employee"));
        return;
    }
    
    if (selected_rows.length > 1) {
        frappe.msgprint(__("Please select only one employee"));
        return;
    }
    
    let employee = selected_rows[0].employee;
    
    frappe.route_options = {
        "employee": employee
    };
    
    frappe.set_route("List", "Employee Disciplinary Action");
}
