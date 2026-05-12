# Mookh.com Invoice & Report Generator

A professional Django app for user-managed invoice and report generation with custom admin dashboard and branded PDFs.

## Features
- User signup with admin approval required before access
- User-entered event details for invoices and reports
- Professional PDF generation with company branding, colors, and tables
- Download and submit documents to the admin
- Custom admin dashboard showing key metrics and recent activity
- Admin can review pending users, invoices, and reports via Django admin

## Recent Enhancements
- **Custom Admin Dashboard**: Overview of pending approvals, submitted documents, and recent activity
- **Professional PDF Branding**: Enhanced PDFs with company headers, colored tables, borders, and professional layout
- **Improved UI**: Better styling and user experience throughout the application

## Setup

1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Run database migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

4. Create an admin user

```powershell
python manage.py createsuperuser
```

5. Start the development server

```powershell
python manage.py runserver
```

6. Open the app in your browser

- User site: `http://127.0.0.1:8000/`
- Admin site: `http://127.0.0.1:8000/admin/` (custom dashboard with metrics)

## Notes
- Admin only needs to approve new users in the Django admin panel.
- Users manually input event details when generating invoices and reports.
- Generated documents are saved and can be downloaded as professional PDF files.
- The admin dashboard provides quick access to all management tasks.
