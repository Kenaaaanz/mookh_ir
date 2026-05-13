# Mookh.com Invoice & Report Generator

A complete Django application for Mookh.com that allows users to sign up, manually add event details, generate branded invoices and reports, download documents, submit them for admin review, and let admins approve users and review submissions.

## System Overview

This app is built with Django and includes:
- User registration and authentication
- Admin approval workflow for new users
- Invoice and report generation with manual event entry
- PDF creation using ReportLab
- Download and submit actions for invoices and reports
- A custom admin dashboard with metrics and activity
- Responsive UI for both desktop and mobile devices

## Core Components

### Models

- `Profile`
  - One-to-one relation with `User`
  - Stores approval status, company name, and phone number

- `Invoice`
  - Stores event invoice data, amounts, status, and generated PDF file
  - Includes `generate_pdf()` to create a branded invoice PDF with user contact details

- `Report`
  - Stores event report data, location, general/technical notes, status, and generated PDF file
  - Includes `generate_pdf()` to create a branded report PDF with user contact details

### Forms

- `SignUpForm`
  - Extends Django `UserCreationForm`
  - Collects `username`, `email`, `first_name`, `last_name`, and `phone`
  - Stores the phone number in the related `Profile`

- `InvoiceForm`
  - Collects `event_name`, `event_date`, `shifts_covered`, `amount_to_be_paid`, and `notes`
  - Uses date and number widgets for better UX

- `ReportForm`
  - Collects `event_name`, `location`, `general_report`, `tech_report`, `additional_notes`

### Views

Key user-facing views:
- `home` - landing page
- `signup` - registration and redirection to pending approval
- `dashboard` - user dashboard showing invoices and reports after approval
- `generate_documents` - form page to create invoices and reports
- `invoice_detail`, `report_detail` - detail pages for view/download/submit
- `download_invoice`, `download_report` - download generated PDF files
- `submit_invoice`, `submit_report` - mark documents as submitted for admin review
- `account_pending` - pending approval message for users before approval

### URLs

User routes are defined in `invoices/urls.py`:
- `/` → home
- `/signup/` → sign-up
- `/login/`, `/logout/` → authentication
- `/dashboard/` → user dashboard
- `/generate/` → create invoices/reports
- `/invoice/<pk>/`, `/report/<pk>/` → document details
- `/invoice/<pk>/download/`, `/report/<pk>/download/` → document downloads
- `/invoice/<pk>/submit/`, `/report/<pk>/submit/` → document submission
- `/pending/` → pending approval notice

Admin site is mounted at `/admin/` and uses a custom admin site instance to show the dashboard.

## Admin Dashboard

The admin dashboard is powered by a custom `MookhAdminSite` in `invoices/admin.py` and includes:
- Pending user approvals
- Submitted invoices count
- Submitted reports count
- Total users count
- Recent submitted invoice/report activity
- Quick links to manage profiles, invoices, and reports

This dashboard is rendered using `invoices/templates/admin/index.html`.

## PDF Generation

The app uses ReportLab to build branded PDFs for invoices and reports with:
- Company logo and header section
- User full name, email, and phone number
- Event details and financial summary
- Professional tables, colors, and footer text

Generated PDFs are stored in `MEDIA_ROOT` under `documents/invoices/` and `documents/reports/`.

## Templates & Frontend

Templates are located in `invoices/templates/invoices/` and include:
- `home.html`
- `signup.html`
- `login.html`
- `dashboard.html`
- `generate_documents.html`
- `view_invoices.html`
- `view_reports.html`
- `account_pending.html`

The base layout is defined in `invoices/templates/invoices/base.html` with a responsive navigation header and mobile-friendly design.

## Settings & Production

Settings are configured in `mookh_project/settings.py` and use `python-decouple` for environment variables:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL` for production databases

Local development uses SQLite by default. Production can use PostgreSQL via `dj_database_url`.

Static and media files:
- `STATIC_URL = '/static/'`
- `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`

Whitenoise is enabled for static file serving in production.

## Environment

Create a `.env` file in the project root with:

```text
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@host:port/dbname  # optional for production
```

## Installation and Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create the `.env` file with `SECRET_KEY` and `DEBUG`.

4. Run database migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

5. (Optional) Create a superuser manually or run the built migration that creates a default `admin` account:

```powershell
python manage.py createsuperuser
```

6. Start the development server:

```powershell
python manage.py runserver
```

7. Access the app:
- User site: `http://127.0.0.1:8000/`
- Admin site: `http://127.0.0.1:8000/admin/`

## Deployment Notes

- Ensure the deployed environment uses the same Django version as local.
- Set `DEBUG=False` in production.
- Provide `SECRET_KEY` and `DATABASE_URL` through environment variables.
- Run `python manage.py collectstatic` before deploying if using static assets.
- Restart the web server after code updates.

## User Workflow

1. User signs up with username, email, full name, and phone.
2. Admin approves the user in the Django admin.
3. Approved user logs in and goes to the dashboard.
4. User enters event information to generate an invoice or report.
5. The system creates and saves a branded PDF.
6. User can download or submit the document.
7. Admin reviews submitted documents in admin.

## Admin Workflow

1. Log in at `/admin/`.
2. Approve or reject new users via the `Profile` model.
3. Review submitted invoices and reports under their models.
4. Use the custom dashboard for quick metrics and activity.

## Notes for Maintenance

- `signals.py` automatically creates a `Profile` for each new `User`.
- `invoices/admin.py` registers models with the custom admin site.
- `invoices/models.py` contains the PDF generation logic.
- `invoices/views.py` contains the workflow logic for creating, downloading, and submitting documents.
- `invoices/forms.py` handles form validation and field rendering.

## Key Files

- `manage.py`
- `mookh_project/settings.py`
- `mookh_project/urls.py`
- `invoices/admin.py`
- `invoices/models.py`
- `invoices/views.py`
- `invoices/forms.py`
- `invoices/signals.py`
- `invoices/urls.py`
- `invoices/templates/invoices/`
- `invoices/templates/admin/index.html`

## Final Thoughts

This system is designed to keep admin work light: approve users, review submitted invoices/reports, and let users handle event entry and document generation. The PDF output is branded, professional, and includes full user contact details.

If you want, I can also add a shorter developer onboarding section or a live deployment checklist. 