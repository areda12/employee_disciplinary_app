# Employee Disciplinary App

Custom ERPNext application for managing employee disciplinary actions and generating comprehensive reports.

## Compatibility

- **ERPNext Version**: v15, v16
- **Frappe Version**: v15, v16
- **Requires**: HRMS module

## Features

- Track employee disciplinary actions
- Generate detailed disciplinary history reports
- Integration with ERPNext HR module

## Installation

1. Get the app from GitHub:
```bash
cd ~/frappe-bench
bench get-app https://github.com/areda12/employee_disciplinary_app
```

2. Install on your site:
```bash
bench --site YOUR_SITE_NAME install-app employee_disciplinary_app
```

3. Restart bench:
```bash
bench restart
```

## Usage

After installation, you'll find the "Employee Disciplinary History" report in your ERPNext HR module.

## License

MIT
