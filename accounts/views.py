# from django.shortcuts import render# views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
import requests

from prospects.tasks import send_email_task
from .forms import *
from django.contrib import messages
# from .models import CompanyUser
from django.urls import reverse
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy

from django.views import View
from django.contrib import messages
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm


# user
def change_password(request, slug):
    user = User.objects.filter(slug=slug).first()
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, f"{user}'s Password updated successfully.")
            return redirect('view-pipeline')
        else:
            # Form errors, including the "Passwords do not match" error, are preserved in the form instance
            messages.error(request, "Could not update user. Try again.")
            return redirect(request.path)
    else:
        form = PasswordChangeForm()
    return render(request, 'home/change_password.html', {'form': form})

@login_required
def change_own_password(request):
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, f"{user}'s Password updated successfully.")
            return redirect('dashboard')
        else:
            # Form errors, including the "Passwords do not match" error, are preserved in the form instance
            messages.error(request, "Could not update user. Try again.")
            return redirect(request.path)
    else:
        form = PasswordChangeForm()
    return render(request, 'home/change_password.html', {'form': form})

# def reset_password_view(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     token_generator = PasswordResetTokenGenerator()
#     if user is not None and token_generator.check_token(user, token):
#         if request.method == 'POST':
#             form = PasswordChangeForm(request.POST)
#             if form.is_valid():
#                 new_password = form.cleaned_data['new_password']
#                 user.set_password(new_password)
#                 user.save()
#                 messages.success(request, "Password updated successfully.")
#                 return redirect('login')  # Redirect to login after successful reset
#             else:
#                 # Form errors, including the "Passwords do not match" error, are preserved in the form instance
#                 messages.error(request, "Could not update user. Try again.")
#                 return redirect(request.path)
#         else:
#             form = PasswordChangeForm()
#         # return render(request, 'home/reset_password.html', {'form': form})
#         return render(request, 'home/change_password.html', {'form': form})
    
#     else:
#         messages.error(request, "The password reset link is invalid or has expired.")
#         return redirect('login')

def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_generator = PasswordResetTokenGenerator()
    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password updated successfully.")
                return redirect('login')  # Redirect to login after successful reset
            else:
                messages.error(request, "Could not update password. Try again.")
                return render(request, 'home/change_password.html', {'form': form})
        else:
            form = SetPasswordForm(user)
        return render(request, 'home/change_password.html', {'form': form})
    
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('login')

## company

class CompanyCreateView(View):

    def get(self, request):
        form = LoanCompanyForm()
        context = {
            'form' : form,
            'page_name' : 'company',
            'sub_page_name' : 'company_create'
        }
        return render(request, 'company/create_company.html', context)

    def post(self, request):
        form = LoanCompanyForm(request.POST, request.FILES)  # Use request.FILES for image upload
        if form.is_valid():
            form.save()  # Save the company form data and logo to the database
            return redirect('company_list')  # Redirect to a success page or list of companies


        context = {
            'form' : form,
            'page_name' : 'company',
            'sub_page_name' : 'company_create'
        }
        return render(request, 'company/create_company.html', context)

# company view
class CompanyListView(View):
    def get(self, request):
        companies = LoanCompany.objects.all()  # Fetch all companies from the database


        context = {
            'companies' : companies,
            'page_name' : 'company',
            'sub_page_name' : 'company_list_view'
        }
        return render(request, 'company/list_companies.html', context)


# company update
class CompanyUpdateView(View):
    def get(self, request, company_id):
        company = get_object_or_404(LoanCompany, id=company_id)  # Get the company by ID or return 404
        form = LoanCompanyForm(instance=company)  # Pre-populate the form with the company data
        context = {
            'company': company,
            'form' : form,
            'page_name' : 'company',
            'sub_page_name' : 'company_update'
        }
        return render(request, 'company/update_company.html', context)

    def post(self, request, company_id):
        company = get_object_or_404(LoanCompany, id=company_id)
        form = LoanCompanyForm(request.POST, request.FILES, instance=company)  # Include request.FILES for the logo field
        if form.is_valid():
            form.save()  # Save the updated company data
            return redirect('company_list')  # Redirect to the list of companies after updating

        context = {
            'company': company,
            'form' : form,
            'page_name' : 'company',
            'sub_page_name' : 'company_update'
        }
        return render(request, 'company/update_company.html', context)






def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        form.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                # return redirect(reverse('prospect_list')) # Redirect to a desired page after login
                return redirect(reverse('dashboard')) # Redirect to a desired page after login
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

from django.db.models import Count, Sum, F, Q
from datetime import datetime, timedelta

@login_required
def dashboard_view(request):
    loan_companies = LoanCompany.objects.all()

    if not ("can_perform_admin_functions" in request.user.permissions or "can_view_dashboard" in request.user.permissions):
        if "can_complete_asset_valuation_details" in request.user.permissions:
            return redirect("prospect_valuation")
        elif "can_view_pipeline" in request.user.permissions:
            return redirect("view-pipeline")

    # Aggregations for each status

    form = ActiveLoanCompanyForm(instance=request.user)

    if request.method == "POST":
        form = ActiveLoanCompanyForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"Successfully changed current active loan company to {form.instance.active_company}.")
        else:
            messages.error(request, "Could not modify user details. Try again.")


    # Preparing context with each status data for individual cards
    three_months_ago = datetime.now() - timedelta(days=90)



    context_data = {
        "page_name": "dashboard",
        'loan_companies': loan_companies,
        "total_principal_released": 0,
        "total_principal_released_this_year": 0,
        "total_principal_released_this_month": 0,
        "total_collections": 0,
        "total_collections_this_year": 0,
        "total_collections_this_month": 0,
        "total_outstanding_principal_open": 0,
        "total_outstanding_interest_open_loans": 0,
        "form":form
    }


    return render(request, 'home/dashboard.html', context=context_data)

@login_required
def create_agent_view(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agent_list')  # Redirect to a list of agents or another page
    else:
        form = AgentForm()
    return render(request, 'agents/create_agent.html', {'form': form})

@login_required
def agent_list_view(request):
    agents = Agent.objects.all()
    context = {'agents': agents,
               'page_name' : 'agent',
               'sub_page_name' : 'agent_list',  
               }
    return render(request, 'agents/view_agents.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout


# @login_required
def home_view(request):
    return render(request, 'registration/home.html')

# @login_required
def executive_dashboard(request):
    return render(request, 'executive/executive_dashboard.html')

# @login_required
def team_leader_dashboard(request):
    return render(request, 'team_leader/team_leader_dashboard.html')

# @login_required
def sales_manager_dashboard(request):
    return render(request, 'sales_manager/sales_manager_dashboard.html')

# @login_required
def operations_reviewer_dashboard(request):
    return render(request, 'operations_reviewer/operations_reviewer_dashboard.html')

# @login_required
def valuer_dashboard(request):
    return render(request, 'valuer/valuer_dashboard.html')
    # return render(request, 'templates/valuer/valuer_dashboard.html')


class RelationOfficerListView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        context["relation_officers"] = RelationOfficer.objects.all()
        context["page_name"] =  "relation_officer"
        context["sub_page_name"] =  "view_ros"

        return render(request, 'ro/relation_officers_list.html', context=context)

class RelationOfficerCreateView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        context["page_name"] =  "relation_officer"
        context["sub_page_name"] =  "create_ro"

        context["form"] = RelationOfficerForm()
        return render(request, 'ro/relation_officer_create.html', context=context)

    def post(self, request):
        context = {}
        form = RelationOfficerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"Relation Officer {form.instance.name} created successfully.")
            return redirect(reverse_lazy("ro_list"))

        context["form"] = form
        messages.add_message(request, messages.ERROR, "An Error occured. Please verify your data!")
        return render(request, 'ro/relation_officer_create.html', context=context)

class RelationOfficerDetailsView(LoginRequiredMixin, View):
    def get(self, request, slug):
        context = {}
        context["page_name"] =  "relation_officer"
        context["sub_page_name"] =  "view_ros"
        ro = RelationOfficer.objects.filter(slug=slug)
        if not ro:
            messages.add_message(request, messages.ERROR, "An Error occured. Record not found!")
            return redirect(reverse_lazy("ro_list"))

        context["relation_officer"] = ro.first()

        return render(request, 'ro/relation_officers_details.html', context=context)


class RelationOfficerEditView(LoginRequiredMixin, View):
    def get(self, request, slug):
        context = {}
        context["page_name"] =  "relation_officer"
        context["sub_page_name"] =  "create_ro"
        ro = RelationOfficer.objects.filter(slug=slug)
        if not ro:
            messages.add_message(request, messages.ERROR, "An Error occured. Record not found!")
            return redirect(reverse_lazy("ro_list"))

        context["form"] = RelationOfficerForm(instance = ro.first())
        return render(request, 'ro/relation_officer_create.html', context=context)

    def post(self, request, slug):
        context = {}
        ro = RelationOfficer.objects.filter(slug=slug)
        if not ro:
            messages.add_message(request, messages.ERROR, "An Error occured. Record not found!")
            return redirect(reverse_lazy("ro_list"))

        form = RelationOfficerForm(request.POST, instance=ro.first())
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"Relation Officer {form.instance.name} modified successfully.")
            return redirect(reverse_lazy("ro_list"))

        context["form"] = form
        messages.add_message(request, messages.ERROR, "An Error occured. Please verify your data!")
        return render(request, 'ro/relation_officer_create.html', context=context)


# admin view
class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin/front_side_admin_side.html', {'page_name': 'dashboard'})


class RolesListView(LoginRequiredMixin, View):
    template_name = "admin/roles/list.html"
    context = {'page_name': 'dashboard'}

    def get(self, request):
        # only show roles in users active company
        roles = Role.objects.filter(company=request.user.company)
        self.context["roles"] = roles

        return render(request, self.template_name, context=self.context)

class RolesDetailView(LoginRequiredMixin, View):
    template_name = "admin/roles/details.html"
    context = {'page_name': 'dashboard'}

    def get(self, request, slug):
        role = Role.objects.filter(slug=slug)
        if not role:
            return redirect(reverse_lazy("roles_list"))

        role = role.first()
        self.context["role"] = role

        self.context["form"] = RoleForm(instance = role)
        self.context["permissions"] = Permission.objects.all()
        self.context["user_companies"] = request.user.company
        self.context["companies_with_role"] = [role.company for role in Role.objects.filter(name=role.name)]
        return render(request, self.template_name, context=self.context)

    def post(self, request, slug):
        role = Role.objects.filter(slug=slug)
        if not role:
            return redirect(reverse_lazy("roles_list"))

        role = role.first()

        role.name = request.POST.get("name")
        role.save()

        companies = []
        permissions = []
        for name, _ in request.POST.items():
            if 'company_option' in name:
                companies.append(name)
            elif 'permission_option' in name:
                permissions.append(name)


        saved_permissions = role.permissions.all()
        new_permissions = Permission.objects.filter(name__in=[request.POST.get(permission_name) for permission_name in permissions])

        if len(saved_permissions) == len(permissions):
            # no changes were made
            return redirect(reverse_lazy("roles_list"))

        # a change was made, identify if some were added or removed
        elif len(saved_permissions) > len(permissions):
            # some were removed. identify them and remove them from role permissions
            for permission in saved_permissions:
                if permission not in new_permissions:
                    role.permissions.remove(permission)
            role.save()
        else:
            # some were added
            for permission in new_permissions:
                if permission not in saved_permissions:
                    role.permissions.add(permission)
            role.save()

        messages.add_message(request, messages.SUCCESS, f"Successfully modified role {role.name} for {role.company}")

        return redirect(reverse_lazy("roles_list"))


class RolesCreateView(LoginRequiredMixin, View):
    template_name = "admin/roles/create.html"
    context = {'page_name': 'dashboard'}

    def get(self, request):
        self.context["form"] = RoleForm()

        self.context["permissions"] = Permission.objects.all()
        self.context["company"] = request.user.company
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        # add company
        # if no company is selected, return error
        # if multiple companies were selected, create roles in each
        companies = []
        permissions = []
        for name, _ in request.POST.items():
            if 'company_option' in name:
                companies.append(name)
            elif 'permission_option' in name:
                permissions.append(name)

        if not companies:
            messages.add_message(request, messages.ERROR, "Select atleast one company!")
        else:
            for name in companies:
                value = request.POST.get(f"{name}")
                # filter company by name
                company = Company.objects.filter(name=value)
                if company:
                    company = company.first()
                    if Role.objects.filter(name=request.POST.get("name"), company=company):
                        messages.add_message(request, messages.ERROR, f'Role: {request.POST.get("name")} Already exists for {company}')
                    else:
                        role = Role.objects.create(name=request.POST.get("name"), company=company)

                        # add permissions to role
                        for permission in permissions:
                            permission_value = request.POST.get(f"{permission}")
                            # filter permission by name
                            permission = Permission.objects.filter(name=permission_value)
                            if permission:
                                permission = permission.first()
                                role.permissions.add(permission)

                        # save permissions add
                        role.save()
                        messages.add_message(request, messages.SUCCESS, f"Successfully created role {role.name}")
        return redirect(reverse_lazy("roles_list"))


class CreateListView(LoginRequiredMixin, View):
    template_name="admin/users/list.html"
    context = {'page_name': 'dashboard'}

    def get(self, request):
        self.context["users"] = User.objects.filter(company=request.user.company)
        return render(request, self.template_name, context=self.context)



# # Option 1 
# class CreateDetailView(LoginRequiredMixin, View):
#     template_name = "admin/users/details.html"
#     context = {'page_name': 'dashboard'}

#     def get(self, request, slug):
#         user = User.objects.filter(slug=slug)
#         if not user:
#             return redirect(reverse_lazy("users_list"))

#         self.context["user"] = user.first()
#         self.context["form"] = UserUpdateForm(user=request.user, instance=user.first())
#         self.context["password_form"] = PasswordChangeForm()  # Initialize password form
#         return render(request, self.template_name, context=self.context)

#     def post(self, request, slug):
#         user = User.objects.filter(slug=slug)
#         if not user:
#             return redirect(reverse_lazy("users_list"))

#         # Handle the user update form
#         form = UserUpdateForm(request.POST, request.FILES, instance=user.first())
#         if form.is_valid():
#             user = form.save()
#             messages.add_message(request, messages.SUCCESS, f"Successfully modified user {user.name}")
#             return redirect(reverse_lazy("users_list"))  # Redirect to user details after update

#         # Handle the password change form
#         new_password = request.POST.get("new_password")
#         confirm_password = request.POST.get("confirm_password")

#         if new_password != confirm_password:
#             messages.add_message(request, messages.ERROR, "Could not update user. Try again.")
#             return redirect(reverse_lazy("users_details", args=[user.slug]))  # Redirect back to user details

#         user = user.first()
#         user.set_password(new_password)
#         user.save()
#         messages.add_message(request, messages.SUCCESS, f"Password for {user} updated successfully.")
#         return redirect(reverse_lazy("users_details", args=[user.slug]))  # Redirect back to user details


# Option 2 

class CreateDetailView(LoginRequiredMixin, View):
    template_name = "admin/users/details.html"
    context = {'page_name': 'dashboard'}

    def get(self, request, slug):
        user = User.objects.filter(slug=slug).first()
        if not user:
            return redirect(reverse_lazy("users_list"))

        # Initialize both forms and add them to the context
        self.context["user"] = user
        self.context["form"] = UserUpdateForm(user=request.user, instance=user)
        self.context["password_form"] = PasswordChangeForm()
        return render(request, self.template_name, context=self.context)

    def post(self, request, slug):
        user = User.objects.filter(slug=slug).first()
        if not user:
            return redirect(reverse_lazy("users_list"))

        # Check which form is being submitted
        if 'update_user' in request.POST:
            form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                user = form.save()
                messages.add_message(request, messages.SUCCESS, f"Successfully modified user {user.name}")
                return redirect(reverse_lazy("users_list"))
            else:
                self.context["form"] = form

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password']
                user.password = make_password(new_password)
                user.save()
                messages.success(request, f"{user}'s Password updated successfully.")
                return redirect(reverse("users_details", kwargs={'slug': user.slug}))
            else:
                # Form errors, including the "Passwords do not match" error, are preserved in the form instance
                messages.error(request, "Could not update user. Try again.")
                self.context["password_form"] = password_form

        # Reinitialize forms in case of errors to avoid clearing
        self.context["form"] = self.context.get("form", UserUpdateForm(instance=user))
        self.context["password_form"] = self.context.get("password_form", PasswordChangeForm())
        return render(request, self.template_name, context=self.context)



# class CreateCreateView(LoginRequiredMixin, View):
#     template_name="admin/users/create.html"
#     context = {'page_name': 'dashboard'}

#     def get(self, request):
#         self.context["form"] = UserCreateForm(user=request.user)
#         return render(request, self.template_name, context=self.context)


#     def post(self, request):
#         form = UserCreateForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()

#             user.companies.add(request.user.company)
#             user.save()

#             if user.email:
#                 change_password_url = request.build_absolute_uri(
#                     reverse('change_password', args=[user.slug])
#                 )

#                 email = EmailMessage(
#                     "Account Created",
#                     f"Your account has been created successfully. Please login to continue.\n UserName is: {user.username}.  Password: {form.cleaned_data['password']}"
#                     f"To change your password, please Login and click 'Change Password' under 'Settings'. ",
#                     # f"{change_password_url}",
#                     settings.DEFAULT_FROM_EMAIL,
#                     [
#                         user.email,
#                     ],
#                 )
#                 email.send(fail_silently=False)
#             messages.add_message(request, messages.SUCCESS, f"Successfully created user {user.name}")
#             return redirect(reverse_lazy("users_list"))

#         self.context["form"] = form
#         messages.add_message(request, messages.ERROR, "Couldnot create company user. Try again")
#         return render(request, self.template_name, context=self.context)
class CreateCreateView(LoginRequiredMixin, View):
    template_name = "admin/users/create.html"
    context = {'page_name': 'dashboard'}

    def get(self, request):
        self.context["form"] = UserCreateForm(user=request.user)
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            user.company = request.user.company
            user.save()

            if user.email:
                # Generate token and encoded user ID
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Construct the reset password link
                # change_password_url = request.build_absolute_uri(
                #     reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
                # )

                
                # construct the reset password link in production. For loro, bdm and subik.
                base_url_with_port = f"{request.scheme}://{request.get_host().split(':')[0]}:9393"
                change_password_url = base_url_with_port + reverse('reset_password', kwargs={'uidb64': uid, 'token': token})

                subject = "Account Created"
                message = f"Your account has been created successfully. Please log in to continue.\nUsername: {user.username}\nTo set your password, click the following link:\n{change_password_url}"
                email = user.email

                send_email_task(subject, email, message)

            messages.success(request, f"Successfully created user {user.username}")
            return redirect(reverse_lazy("users_list"))

        self.context["form"] = form
        messages.error(request, "Could not create company user. Try again.")
        return render(request, self.template_name, context=self.context)
    
@login_required
def loan_origination(request):
    return render(request, "mobile/loan_origination.html")

@login_required
def loan_collection(request):
    return render(request, "mobile/loan_collection.html")


class LoanCompanyToggleView(LoginRequiredMixin, View):
    template_name = "home/change_company.html"
    context = {'page_name': 'dashboard'}

    def get(self, request):
        form = ActiveLoanCompanyForm()
        self.context['form'] = form
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        form = ActiveLoanCompanyForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            # set user role
        else:
            messages.add_message(request, messages.ERROR, "Couldnot modify user details. Try again")

        self.context['form'] = form
        return render(request, self.template_name, context=self.context)

# class UserCompanyToggleView(LoginRequiredMixin, View):
#     template_name = "home/change_company.html"
#     context = {}

#     def get(self, request):
#         comapany_form = UserActiveCompanyForm()
#         self.context['company_form'] = company_form
#         return render(request, self.template_name, context=self.context)

#     def post(self, request):
#         company_form = UserActiveCompanyForm(request.POST, instance = request.user)
#         if company_form.is_valid():
#             instance = company_form.save()
#             # set user role
#             new_role = Role.objects.filter(name=instance.role.name, company=instance.active_company)
#             if new_role:
#                 instance.role = new_role.first()
#                 instance.save()
#                 messages.add_message(request, messages.SUCCESS, f"User Active Company set to:{instance.active_company} with Role: {instance.role.name}")
#             else:
#                 messages.add_message(request, messages.ERROR, "Couldnot modify user details. Matching Role not found")
#         else:
#             messages.add_message(request, messages.ERROR, "Couldnot modify user details. Try again")

#         self.context['company_form'] = company_form
#         return render(request, self.template_name, context=self.context)




def forgot_my_password_reset(request):
    form = ForgetPasswordForm()
    if request.method == "POST":
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get("email")
            if email:
                user = User.objects.filter(email=email).first()
                if user:
                    if user.email:
                        # Generate token and encoded user ID
                        token_generator = PasswordResetTokenGenerator()
                        token = token_generator.make_token(user)
                        uid = urlsafe_base64_encode(force_bytes(user.pk))

                        # Construct the reset password link
                        change_password_url = request.build_absolute_uri(
                            reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
                        )

                        subject = "PASSWORD RESET LINK"
                        message = f"Your Password reset link has been successfully generated. \nUsername: {user.username}\nClick the following link to reset your password.\nPASSWORD RESET LINK: {change_password_url}"
                        email = user.email

                        send_email_task(subject, email, message)
                        messages.success(request, "Password reset link sent to your email.")
                        return redirect("login")
                    else:
                        messages.error(request, "User email is not valid.")
                else:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Please provide an email address.")
        else:
            messages.error(request, "Invalid form submission.")
    
    return render(request, 'home/forgot_password_reset.html', {'form': form})

    

