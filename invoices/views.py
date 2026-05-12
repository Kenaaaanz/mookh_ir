from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import InvoiceForm, ReportForm, SignUpForm
from .models import Invoice, Report


def home(request):
    return render(request, 'invoices/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
            messages.success(request, 'Your account has been created and is pending admin approval.')
            return redirect('account_pending')
    else:
        form = SignUpForm()
    return render(request, 'invoices/signup.html', {'form': form})


@login_required
def dashboard(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.approved:
        return redirect('account_pending')

    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    reports = Report.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'invoices/dashboard.html', {'invoices': invoices, 'reports': reports})


@login_required
def account_pending(request):
    if hasattr(request.user, 'profile') and request.user.profile.approved:
        return redirect('dashboard')
    return render(request, 'invoices/account_pending.html')


@login_required
def generate_documents(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.approved:
        return redirect('account_pending')

    invoice_form = InvoiceForm()
    report_form = ReportForm()

    if request.method == 'POST':
        if 'create_invoice' in request.POST:
            invoice_form = InvoiceForm(request.POST)
            if invoice_form.is_valid():
                invoice = invoice_form.save(commit=False)
                invoice.user = request.user
                invoice.total_amount = invoice.amount_to_be_paid * invoice.shifts_covered
                invoice.status = 'draft'
                invoice.save()
                invoice.generate_pdf()
                invoice.save()
                messages.success(request, 'Invoice generated successfully. You can submit or download it now.')
                return redirect('invoice_detail', pk=invoice.pk)
        elif 'create_report' in request.POST:
            report_form = ReportForm(request.POST)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.user = request.user
                report.status = 'draft'
                report.save()
                report.generate_pdf()
                report.save()
                messages.success(request, 'Report generated successfully. You can submit or download it now.')
                return redirect('report_detail', pk=report.pk)

    return render(request, 'invoices/generate_documents.html', {
        'invoice_form': invoice_form,
        'report_form': report_form,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    return render(request, 'invoices/view_invoices.html', {'invoice': invoice})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    return render(request, 'invoices/view_reports.html', {'report': report})


@login_required
def download_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    if not invoice.pdf_file:
        invoice.generate_pdf()
        invoice.save()
    try:
        return FileResponse(invoice.pdf_file.open('rb'), as_attachment=True, filename=f'invoice_{invoice.pk}.pdf')
    except FileNotFoundError:
        raise Http404('Invoice file not found.')


@login_required
def download_report(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    if not report.pdf_file:
        report.generate_pdf()
        report.save()
    try:
        return FileResponse(report.pdf_file.open('rb'), as_attachment=True, filename=f'report_{report.pk}.pdf')
    except FileNotFoundError:
        raise Http404('Report file not found.')


@login_required
def submit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    invoice.status = 'submitted'
    invoice.save()
    messages.success(request, 'Invoice submitted for admin review.')
    return redirect(reverse('invoice_detail', kwargs={'pk': pk}))


@login_required
def submit_report(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    report.status = 'submitted'
    report.save()
    messages.success(request, 'Report submitted for admin review.')
    return redirect(reverse('report_detail', kwargs={'pk': pk}))
