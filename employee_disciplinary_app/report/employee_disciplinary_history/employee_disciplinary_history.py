# Copyright (c) 2024, [Your Company] and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, now_datetime, date_diff
from datetime import datetime, timedelta

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    
    return columns, data, None, chart

def get_columns(filters):
    """Define report columns"""
    columns = [
        {
            "label": _("Employee ID"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 150
        },
        {
            "label": _("Total Incidents"),
            "fieldname": "total_incidents",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Total Points"),
            "fieldname": "total_points",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Minor"),
            "fieldname": "minor_count",
            "fieldtype": "Int",
            "width": 70
        },
        {
            "label": _("Moderate"),
            "fieldname": "moderate_count",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Major"),
            "fieldname": "major_count",
            "fieldtype": "Int",
            "width": 70
        },
        {
            "label": _("Critical"),
            "fieldname": "critical_count",
            "fieldtype": "Int",
            "width": 70
        },
        {
            "label": _("Verbal Warnings"),
            "fieldname": "verbal_warnings",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Written Warnings"),
            "fieldname": "written_warnings",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Suspensions"),
            "fieldname": "suspensions",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Total Suspension Days"),
            "fieldname": "total_suspension_days",
            "fieldtype": "Int",
            "width": 140
        },
        {
            "label": _("Final Warnings"),
            "fieldname": "final_warnings",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Retraining Sessions"),
            "fieldname": "retraining_count",
            "fieldtype": "Int",
            "width": 130
        },
        {
            "label": _("Repeats (30d)"),
            "fieldname": "repeats_30",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Repeats (90d)"),
            "fieldname": "repeats_90",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Last Incident Date"),
            "fieldname": "last_incident_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Days Since Last"),
            "fieldname": "days_since_last",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Risk Level"),
            "fieldname": "risk_level",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        }
    ]
    
    return columns

def get_data(filters):
    """Fetch and process data"""
    
    # Build conditions
    conditions = get_conditions(filters)
    
    # Get all disciplinary actions
    actions = frappe.db.sql(f"""
        SELECT 
            employee,
            employee_name,
            department,
            incident_datetime,
            severity,
            points,
            action_type,
            suspension_days,
            violation_type,
            violation_code,
            name
        FROM `tabEmployee Disciplinary Action`
        WHERE docstatus < 2
        {conditions}
        ORDER BY employee, incident_datetime DESC
    """, filters, as_dict=1)
    
    if not actions:
        return []
    
    # Group by employee
    employee_data = {}
    
    for action in actions:
        emp_id = action.employee
        
        if emp_id not in employee_data:
            employee_data[emp_id] = {
                'employee': emp_id,
                'employee_name': action.employee_name,
                'department': action.department,
                'total_incidents': 0,
                'total_points': 0,
                'minor_count': 0,
                'moderate_count': 0,
                'major_count': 0,
                'critical_count': 0,
                'verbal_warnings': 0,
                'written_warnings': 0,
                'suspensions': 0,
                'total_suspension_days': 0,
                'final_warnings': 0,
                'retraining_count': 0,
                'repeats_30': 0,
                'repeats_90': 0,
                'last_incident_date': None,
                'days_since_last': 0,
                'incidents': []
            }
        
        # Accumulate data
        emp = employee_data[emp_id]
        emp['total_incidents'] += 1
        emp['total_points'] += action.points or 0
        emp['incidents'].append(action)
        
        # Count by severity
        if action.severity == 'Minor':
            emp['minor_count'] += 1
        elif action.severity == 'Moderate':
            emp['moderate_count'] += 1
        elif action.severity == 'Major':
            emp['major_count'] += 1
        elif action.severity == 'Critical':
            emp['critical_count'] += 1
        
        # Count by action type
        if action.action_type == 'Verbal Warning':
            emp['verbal_warnings'] += 1
        elif action.action_type == 'Written Warning':
            emp['written_warnings'] += 1
        elif action.action_type == 'Suspension (days)':
            emp['suspensions'] += 1
            emp['total_suspension_days'] += action.suspension_days or 0
        elif action.action_type == 'Final Warning':
            emp['final_warnings'] += 1
        elif action.action_type == 'Retraining/Toolbox Talk':
            emp['retraining_count'] += 1
        
        # Track last incident
        incident_date = getdate(action.incident_datetime)
        if not emp['last_incident_date'] or incident_date > emp['last_incident_date']:
            emp['last_incident_date'] = incident_date
    
    # Calculate additional metrics
    today = getdate()
    
    for emp_id, emp in employee_data.items():
        # Days since last incident
        if emp['last_incident_date']:
            emp['days_since_last'] = date_diff(today, emp['last_incident_date'])
        
        # Calculate repeats in 30 and 90 days
        emp['repeats_30'] = count_repeats(emp['incidents'], 30)
        emp['repeats_90'] = count_repeats(emp['incidents'], 90)
        
        # Determine risk level
        emp['risk_level'] = calculate_risk_level(emp)
        
        # Determine status
        emp['status'] = determine_status(emp)
    
    # Convert to list and sort
    data = list(employee_data.values())
    
    # Sort by total points (highest first)
    data.sort(key=lambda x: x['total_points'], reverse=True)
    
    return data

def count_repeats(incidents, days):
    """Count incidents that have repeats within specified days"""
    repeat_count = 0
    
    for i, incident in enumerate(incidents):
        incident_date = getdate(incident.incident_datetime)
        violation_type = incident.violation_type
        
        # Check if same violation type occurred within X days before
        for j in range(i + 1, len(incidents)):
            other_date = getdate(incidents[j].incident_datetime)
            
            if incidents[j].violation_type == violation_type:
                days_diff = date_diff(incident_date, other_date)
                
                if 0 < days_diff <= days:
                    repeat_count += 1
                    break  # Count each incident only once as a repeat
    
    return repeat_count

def calculate_risk_level(emp):
    """Calculate employee risk level based on various factors"""
    
    # Scoring system
    score = 0
    
    # Points-based scoring
    if emp['total_points'] >= 20:
        score += 5
    elif emp['total_points'] >= 15:
        score += 4
    elif emp['total_points'] >= 10:
        score += 3
    elif emp['total_points'] >= 5:
        score += 2
    elif emp['total_points'] > 0:
        score += 1
    
    # Critical/Major incidents
    score += emp['critical_count'] * 3
    score += emp['major_count'] * 2
    
    # Recent activity (within 30 days)
    if emp['days_since_last'] <= 30:
        score += 2
    elif emp['days_since_last'] <= 90:
        score += 1
    
    # Repeat violations
    score += emp['repeats_30'] * 2
    score += emp['repeats_90']
    
    # Final warnings
    score += emp['final_warnings'] * 3
    
    # Suspensions
    score += emp['suspensions'] * 2
    
    # Determine risk level
    if score >= 15:
        return "🔴 Critical Risk"
    elif score >= 10:
        return "🟠 High Risk"
    elif score >= 5:
        return "🟡 Moderate Risk"
    elif score >= 2:
        return "🟢 Low Risk"
    else:
        return "⚪ Minimal Risk"

def determine_status(emp):
    """Determine current employee disciplinary status"""
    
    if emp['final_warnings'] > 0:
        if emp['days_since_last'] <= 90:
            return "⚠️ Final Warning - Active"
        else:
            return "📋 Final Warning - Monitoring"
    
    if emp['suspensions'] > 0:
        if emp['days_since_last'] <= 60:
            return "⏸️ Post-Suspension Review"
        
    if emp['written_warnings'] > 0:
        if emp['days_since_last'] <= 30:
            return "⚠️ Written Warning - Active"
        elif emp['days_since_last'] <= 90:
            return "📋 Written Warning - Monitoring"
    
    if emp['total_incidents'] >= 5:
        return "👁️ High Frequency - Watch"
    
    if emp['repeats_30'] > 0:
        return "🔄 Repeat Offender"
    
    if emp['days_since_last'] <= 30:
        return "📌 Recent Incident"
    
    if emp['days_since_last'] > 180:
        return "✅ Good Standing"
    
    return "📊 Standard Monitoring"

def get_conditions(filters):
    """Build SQL conditions from filters"""
    conditions = []
    
    if filters.get("employee"):
        conditions.append("employee = %(employee)s")
    
    if filters.get("department"):
        conditions.append("department = %(department)s")
    
    if filters.get("from_date"):
        conditions.append("DATE(incident_datetime) >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("DATE(incident_datetime) <= %(to_date)s")
    
    if filters.get("severity"):
        conditions.append("severity = %(severity)s")
    
    if filters.get("min_incidents"):
        # This will be handled post-query
        pass
    
    if filters.get("risk_level"):
        # This will be handled post-query
        pass
    
    return " AND " + " AND ".join(conditions) if conditions else ""

def get_chart_data(data, filters):
    """Generate chart data for visualization"""
    
    if not data:
        return None
    
    # Risk level distribution
    risk_distribution = {
        "🔴 Critical Risk": 0,
        "🟠 High Risk": 0,
        "🟡 Moderate Risk": 0,
        "🟢 Low Risk": 0,
        "⚪ Minimal Risk": 0
    }
    
    for emp in data:
        risk_level = emp.get('risk_level', '⚪ Minimal Risk')
        risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
    
    chart = {
        "data": {
            "labels": list(risk_distribution.keys()),
            "datasets": [
                {
                    "name": "Employees by Risk Level",
                    "values": list(risk_distribution.values())
                }
            ]
        },
        "type": "donut",
        "height": 300,
        "colors": ["#dc3545", "#fd7e14", "#ffc107", "#28a745", "#6c757d"]
    }
    
    return chart
