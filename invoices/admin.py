from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator

from .models import Invoice, Profile, Report


class MookhAdminSite(AdminSite):
    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'pending_users': Profile.objects.filter(approved=False).count(),
            'submitted_invoices': Invoice.objects.filter(status='submitted').count(),
            'submitted_reports': Report.objects.filter(status='submitted').count(),
            'total_users': Profile.objects.count(),
        })
        return super().index(request, extra_context=extra_context)


admin_site = MookhAdminSite(name='admin')


@staff_member_required
def admin_dashboard(request):
    # Stats
    pending_users = Profile.objects.filter(approved=False).count()
    submitted_invoices = Invoice.objects.filter(status='submitted').count()
    submitted_reports = Report.objects.filter(status='submitted').count()
    total_users = Profile.objects.count()

    # Recent activity (last 10 items)
    recent_invoices = Invoice.objects.filter(status='submitted').order_by('-created_at')[:5]
    recent_reports = Report.objects.filter(status='submitted').order_by('-created_at')[:5]

    recent_activity = []

    for invoice in recent_invoices:
        recent_activity.append({
            'type': 'Invoice Submitted',
            'description': f'{invoice.event_name}',
            'user': invoice.user.username,
            'date': invoice.created_at.strftime('%b %d, %H:%M'),
            'model': 'invoice',
            'id': invoice.id
        })

    for report in recent_reports:
        recent_activity.append({
            'type': 'Report Submitted',
            'description': f'{report.event_name}',
            'user': report.user.username,
            'date': report.created_at.strftime('%b %d, %H:%M'),
            'model': 'report',
            'id': report.id
        })

    # Sort by date (most recent first)
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]

    context = {
        'pending_users': pending_users,
        'submitted_invoices': submitted_invoices,
        'submitted_reports': submitted_reports,
        'total_users': total_users,
        'recent_activity': recent_activity,
        'title': 'Mookh.com Admin Dashboard',
    }

    return render(request, 'admin/index.html', context)


@admin.register(Profile, site=admin_site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'approved', 'company_name', 'phone']
    list_filter = ['approved']
    search_fields = ['user__username', 'user__email', 'company_name']


@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event_name', 'event_date', 'status', 'created_at']
    list_filter = ['status', 'event_date']
    search_fields = ['event_name', 'user__username']


@admin.register(Report, site=admin_site)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event_name', 'location', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['event_name', 'location', 'user__username']
