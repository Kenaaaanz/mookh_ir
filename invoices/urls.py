from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='invoices/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate/', views.generate_documents, name='generate_documents'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('report/<int:pk>/', views.report_detail, name='report_detail'),
    path('invoice/<int:pk>/download/', views.download_invoice, name='download_invoice'),
    path('report/<int:pk>/download/', views.download_report, name='download_report'),
    path('invoice/<int:pk>/submit/', views.submit_invoice, name='submit_invoice'),
    path('report/<int:pk>/submit/', views.submit_report, name='submit_report'),
    path('pending/', views.account_pending, name='account_pending'),
]
