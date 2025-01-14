from django.urls import path
from .views import *

urlpatterns = [
    # path('', home_view, name='home'),  # Home page
    path('login/', login_view, name='login'),
    path('', dashboard_view, name='dashboard'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create-company/', CompanyCreateView.as_view(), name='create_company'),
    path('company-list/', CompanyListView.as_view(), name='company_list'),
    path('logout/', logout_view, name='logout'),
    path('executive_dashboard/', executive_dashboard, name='executive_dashboard'),
    path('valuer_dashboard/', valuer_dashboard, name='valuer_dashboard'),
    path('create_company', CompanyCreateView.as_view(), name='create_company'),
    path('list-companies/', CompanyListView.as_view(), name='company_list'),
    path('update_company/<int:company_id>/', CompanyUpdateView.as_view(), name='update_company'),

    # admin
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),


    path("roles/", RolesListView.as_view(), name="roles_list"),
    path("roles/<str:slug>/detail", RolesDetailView.as_view(), name="roles_details"),
    path("roles/create/", RolesCreateView.as_view(), name="roles_create"),

    path("users/", CreateListView.as_view(), name="users_list"),
    path("users/<str:slug>/detail", CreateDetailView.as_view(), name="users_details"),
    path("users/create/", CreateCreateView.as_view(), name="users_create"),
    path("company/toggle/", LoanCompanyToggleView.as_view(), name="company_toggle"),
    path('user/<str:slug>/change-password/', change_password, name='change_password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password_view, name='reset_password'),
    path('user/reset-your-password/', change_own_password, name='reset_your_password'),




    # FOR MOBILE PURPOSES ONLY
    path("loan_origination", loan_origination, name="loan_origination"),
    path("loan_collection", loan_collection, name="loan_collection"),
]
