from django.contrib import admin
from django.contrib.admin import AdminSite

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


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'approved', 'company_name', 'phone']
    list_filter = ['approved']
    search_fields = ['user__username', 'user__email', 'company_name']


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event_name', 'event_date', 'status', 'created_at']
    list_filter = ['status', 'event_date']
    search_fields = ['event_name', 'user__username']


class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event_name', 'location', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['event_name', 'location', 'user__username']


admin_site.register(Profile, ProfileAdmin)
admin_site.register(Invoice, InvoiceAdmin)
admin_site.register(Report, ReportAdmin)
