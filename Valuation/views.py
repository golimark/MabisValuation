from datetime import datetime
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView
import requests
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField,Q
from django.contrib import messages
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
import json
from accounts.models import *
from django.db.models import Prefetch


# START OF VIEWS FOR HANDLING THE VALUATIONS SECTION FROM THE BASE.HTML
# View to list all prospects for.meant to enable accessing the prospect details where buttons for handling prospects with different
#  statuses from Pending to Review
class ValuationProspectListView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/prospect_list_valuation.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to exclude prospects with 'Pipeline' status
        # and order by 'New' status first, then by 'created_at'
        return Prospect.objects.exclude(status='Pipeline').annotate(
            is_new=Case(
                When(status='New', then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('is_new', 'updated_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "payment_valuation"
        return context

# view for showing prospects with 'Pending' status to enable access to customized buttons
class ValuationProspectPendingView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/pending_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Pending' status
        return Prospect.objects.filter(status='Pending').order_by('created_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "valuation_review"
        return context

# view for displaying details for a prospect with accessibility to customized buttons
class ValuationProspectDetailView(LoginRequiredMixin, DetailView):
    model = Prospect
    template_name = 'valuations/prospect_detail.html'
    context_object_name = 'prospect'
    lookup_value = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get vehicle assets
        vehicle_asset = VehicleAsset.objects.filter(prospect=self.object)
        if vehicle_asset:
            context['vehicle_evaluation_report'] = VehicleEvaluationReport
        # context['evaluation_report'] = EvaluationReport.objects.filter(prospect=self.object).first()  # Get the first/only report

        prospect = self.object

        # check if prospect has assets
        # car asset
        vehicle_assets = VehicleAsset.objects.filter(prospect=prospect)
        if vehicle_assets:
            context['vehicle_asset'] = vehicle_assets

            # get evaluations
            context['v_evaluation_reports'] = VehicleEvaluationReport.objects.filter(vehicle__in=vehicle_assets)


        # land asset
        land_assets = LandAsset.objects.filter(prospect=prospect)
        if land_assets:
            context['land_asset'] = land_assets

        users_with_permission = User.objects.filter(
            role__permissions__code='can_be_valuers',
            active_company=self.request.user.company
        )
        print(users_with_permission)
        context["valuers"] =  users_with_permission

        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "valuation_review"

        return context
        
    def post(self, request, *args, **kwargs):
        prospect = self.get_object()
        print(prospect, 'prospect')
        print('\n\n\n\n')
        valuer_id = request.POST.get("valuer")

        try:
            valuer = User.objects.get(
                id=valuer_id,
                role__permissions__code='can_be_valuers',
                active_company=request.user.company
            )
            # Assign the valuer to the prospect and save
            prospect.valuer_assigned = valuer
            prospect.valuer_assigned_on = timezone.now()
            prospect.save()
            messages.success(request, "Valuer assigned successfully.")
        except User.DoesNotExist:
            messages.error(request, "Selected valuer is invalid or does not have permission.")

        # Redirect back to the same page after processing
        return redirect(reverse('valuation_prospect_detail', kwargs={'slug': prospect.slug}))


# View to display prospects with 'Valuation' status
class ProspectValuationView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/valuation_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Failed' status
        return Prospect.objects.filter(status='Valuation').order_by('created_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "valuation_requests"
        return context


# View for displaying prospects with 'Review' status
class ProspectReviewView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/review_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Failed' status
        return Prospect.objects.filter(status='Review').order_by('created_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "Failed_prospects"
        return context

# View to set a prospect status to 'Decline' when status is 'Pending'

@login_required
def DeclineView(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)

    if request.method == 'POST':
        decline_reason = request.POST.get('declinereason', '')
        if decline_reason:
            prospect.status = 'Declined'
            prospect.decline_reason = f"Valuation-{decline_reason}"
            prospect.save()
            messages.success(request, 'Prospect declined successfully.')
        else:
            messages.error(request, 'Decline reason is required.')
            return redirect(reverse('valuation_prospect_detail', kwargs={'slug': prospect.slug}))

        context = {
            "page_name": "valuation",
            'prospect': prospect,
            "sub_page_name": "declined_valuation_prospects"
        }

        return render(request, 'prospects/prospect_list.html', context=context)

    context = {
        "page_name": "valuation",
        'prospect': prospect,
        "sub_page_name": "declined_valuation_prospects"
    }

    return render(request, 'prospects/decline_form.html', context=context)


# check two
# from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from .models import Prospect
import json


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count

def get_least_assigned_valuer(company):
        users_with_permission = User.objects.filter(
            role__permissions__code='can_be_valuers',
            active_company=company
        )

        assignments = Prospect.objects.filter(valuer_assigned__in=users_with_permission).values('valuer_assigned').annotate(count=Count('valuer_assigned')).order_by('count')        

        if assignments:
            # Get the valuer with the least assignments
            least_assigned_valuer_id = assignments[0]['valuer_assigned']
            return User.objects.get(id=least_assigned_valuer_id)
        else:
            # If no assignments, return the first valuer
            return users_with_permission.first()


@login_required
def prospect_in_valuation(request, slug):
    if request.method == "POST":
        print("Received POST request for valuation assignment")
        data = json.loads(request.body)
        payment_id = data.get('payment_id', None)
        if not payment_id:
            print("No payment ID provided in request")
            return JsonResponse({'error': 'No payment ID provided.'}, status=403)

        # Retrieve the single prospect to verify and assign
        prospect = Prospect.objects.filter(slug=slug, proof_of_payment_id=payment_id).first()
        if not prospect:
            print(f"No prospect found with slug {slug} and payment ID {payment_id}")
            return JsonResponse({'error': 'Invalid payment ID.'}, status=403)

        # Update prospect's status to "Payment Verified"
        print(f"Prospect found: {prospect.name}")
        prospect.status = "Payment Verified"
        prospect.payment_verified_on = datetime.now()
        prospect.payment_verified_by = request.user
    
        prospect.save()
        print(f"Prospect status updated to Payment Verified for {prospect.name}")

        # Retrieve all users with 'can_be_valuers' permission in the user's active company
        users_with_permission = User.objects.filter(
            # role__permissions__code='can_view_valuation_requests',
            role__permissions__code='can_be_valuers',
            company=request.user.company
        )
        print(f"Users with 'can_be_valuers' permission: {[user.name for user in users_with_permission]}")

        # Get all prospects with an assigned valuer
        valuer_assignments = (
            Prospect.objects
            .exclude(valuer_assigned=None)  # Exclude unassigned prospects
            .values('valuer_assigned')  # Group by each valuer
            .annotate(assign_count=Count('valuer_assigned'))  # Count their assignments
            .order_by('assign_count')  # Sort by the count in ascending order
        )
        print("Valuer assignments (valuer ID -> count):", {assign['valuer_assigned']: assign['assign_count'] for assign in valuer_assignments})

        # Check the current valuer assignment counts and find the least assigned valuer
        valuer_assignment_dict = {assign['valuer_assigned']: assign['assign_count'] for assign in valuer_assignments}
        least_assigned_valuer = None
        for valuer in users_with_permission:
            # If the valuer doesn't have an assignment yet, they should be first in line
            if valuer.id not in valuer_assignment_dict:
                least_assigned_valuer = valuer
                break
            # If valuer has the least assignments, choose them
            if least_assigned_valuer is None or valuer_assignment_dict[valuer.id] < valuer_assignment_dict.get(least_assigned_valuer.id, float('inf')):
                least_assigned_valuer = valuer

        # If a least assigned valuer was found, assign them to the prospect
        if least_assigned_valuer:
            print(f"Selected valuer: {least_assigned_valuer.name} (ID: {least_assigned_valuer.id})")
            prospect.valuer_assigned = least_assigned_valuer
            prospect.valuer_assigned_on = timezone.now()
            prospect.save()
            print(f"Valuer {least_assigned_valuer.name} assigned to prospect {prospect.name}")
            return JsonResponse({'success': 'Payment verified and valuer assigned.'})
        else:
            print("No valuer found to assign")
            return JsonResponse({'error': 'No  available.'}, status=404)

    print("Received invalid request method (not POST)")
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# class AssignRelationOfficerForm(forms.ModelForm):
#     class Meta:
#         model = LoanAccount
#         fields = ["relation_officer"]

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
#         ro_role = Role.objects.filter(Q(permissions__code="can_create_payment_as_ro"))
#         ad_role = Role.objects.filter(Q(permissions__code="can_perform_admin_functions"))

#         queryset = User.objects.filter(Q(role__in=ro_role), ~Q(role__in=ad_role))

#         if user:
#             queryset = queryset.filter(company=user.company)

#         self.fields['relation_officer'].queryset = queryset



@login_required
def set_valuation(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)

    # Change the status to 'Valuation'
    prospect.submitted_for_valuation_by = request.user
    prospect.submitted_for_valuation_on = datetime.now()
    prospect.status = 'Valuation'
    prospect.save()  # Save the updated prospect instance to the database


    return redirect('prospect_valuation')




@login_required
def set_valuation_supervisor(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)

    # Change the status to 'Valuation'
    # prospect.submitted_for_valuation_by = request.user
    # prospect.submitted_for_valuation_on = datetime.now()
    prospect.status = 'Valuation Supervisor'
    prospect.save()  # Save the updated prospect instance to the database


    return redirect('prospect_valuation')



# # View for adding evaluation report details for a particular prospect
# @login_required
# def add_valuation_report_details(request, slug):
#     prospect = get_object_or_404(Prospect, slug=slug)
#     # vehicle = get_object_or_404(VehicleAsset, id=vehicle.id)



#     context = {
#         "page_name": "valuation",
#         'prospect': prospect,
#         "sub_page_name" : "declined_valuation_prospects"
#     }

#     if request.method == 'POST':
#         # Vehicles
#         v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
#         if not v_reports:
#             form = VehicleEvaluationReportForm(request.POST, request.FILES, prospect=prospect)
#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.prospect = prospect
#                 # prospect.status = 'Valuation Supervisor'
                
#                 form.save()

#                 # fields = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect).first()
#                 # fields = v_reports.first()
#                 # fields_data = {}
#                 # Save market_value and forced_sale to the fields JSONField as specified
#                 form.fields = {
#                     "market_value": form.market_value,
#                     "forced_sale": form.forced_sale
#                 }
#                 print(form.fields)
#                 form.save()  # Now save the changes to the fields JSONField

#                 prospect.status = 'Valuation Supervisor'
#                 prospect.valuation_submitted_on = datetime.now()
#                 prospect.valuation_submitted_by = request.user
#                 prospect.save()
#                 # Redirect to the 'valuation_prospect_detail' page
#                 messages.add_message(request, messages.SUCCESS, "Asset Valuation submitted successfully")
#                 return redirect('valuation_prospect_detail', pk=prospect.id)
#             else:
#                 messages.add_message(request, messages.ERROR, "ERROR MODIFYING RECORDS. TRY AGAIN!!")
#         else:
#             # save edited data
#             submitted_report_id = request.GET.get("form_id")
#             if submitted_report_id:
#                 report = VehicleEvaluationReport.objects.filter(pk=submitted_report_id)
#                 # save updated data
#                 if not report:
#                     messages.add_message(request, messages.ERROR, "REPORT NOT FOUND. TRY AGAIN!")
#                 else:
#                     form = VehicleEvaluationReportForm(request.POST, request.FILES, instance=report.first(), prospect=prospect)
#                     if form.is_valid():
#                         form = form.save(commit=False)
#                         form.prospect = prospect
#                         # form.prospect.status = 'Valuation Supervisor'
#                         form.save()
#                         # prospect.status = 'Review'
#                         prospect.status = 'Valuation Supervisor'
#                         prospect.valuation_submitted_on = datetime.now()
#                         prospect.valuation_submitted_by = request.user
#                         messages.add_message(request, messages.SUCCESS, "RECORDS MODIFIED SUCCESSFULLY")

#             # redirect to details page if form id is found or not
#             return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

#     else:
#         # check if there is editing report
#         #
#         #
#         # Vehicles
#         v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
        
#         if v_reports:
#             # prospect.status = 'Valuation Supervisor' --> don't put prospect status here.
#             context["v_reports"] = [{"form": VehicleEvaluationReportForm(instance=report, prospect=prospect), "report": report, } for report in v_reports]
#         else:
#             context["create_vehicle_report_form"] = VehicleEvaluationReportForm(prospect=prospect)


#         # land
#         #
#         #
#         #
#         #

#     return render(request, 'valuations/evaluation_report_form.html', context=context)


# View for viewing the evaluation report
@login_required
def view_valuation_report(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)
    # for now, vehicle evaluation report
    evaluation_report = get_object_or_404(VehicleEvaluationReport, prospect=prospect)

    context = {
        "page_name": "valuation",
        'prospect': prospect,
        'evaluation_report': evaluation_report
    }

    return render(request, 'valuations/prospect_detail.html', context=context)




# View for submitting the report
# @login_required
# def submit_report(request, prospect_id):
#     prospect = get_object_or_404(Prospect, pk=prospect_id)
#     evaluation_report = get_object_or_404(EvaluationReport, prospect=prospect)

#     if request.method == 'POST':
#         prospect.status = 'Review'
#         prospect.save()
#         return redirect('prospect_detail', prospect_id=prospect.pk)
#         # return redirect('valuations_prospect_list')
#     return render(request, 'valuations/submit_report.html', {'prospect': prospect, 'evaluation_report': evaluation_report})
@login_required
def submit_report(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)

    context = {
        "page_name": "valuation",
        'prospect': prospect,
    }

    # check if prospect has assets
    # car asset
    vehicle_assets = VehicleAsset.objects.filter(prospect=prospect)
    if vehicle_assets:
        context['vehicle_asset'] = vehicle_assets
        # get evaluations
        context['v_evaluation_reports'] = VehicleEvaluationReport.objects.filter(vehicle__in=vehicle_assets)

    # land asset
    land_assets = LandAsset.objects.filter(prospect=prospect)
    if land_assets:
        context['land_asset'] = land_assets
        context['l_evaluation_reports'] = LandEvaluationReport.objects.filter(vehicle__in=vehicle_assets)

    if not (context.get('l_evaluation_reports') or context.get('v_evaluation_reports')):
        # Handle case where there are no evaluation reports
        return redirect('valuation_prospect_detail', slug=slug)


    if request.method == 'POST':
        prospect.status = 'Review'
        prospect.valuation_submitted_on = datetime.now()
        prospect.valuation_submitted_by = request.user
        prospect.save()
        # return redirect('valuation_prospect_detail', pk=prospect.id)
        return redirect('prospect_valuation')

    return render(request, 'valuations/submit_report.html', context=context)


@login_required
def print_valuation_report(request, slug):
    # Get the prospect and related evaluation report
    prospect = get_object_or_404(Prospect, slug=slug)
    evaluation_report = get_object_or_404(VehicleEvaluationReport, prospect=prospect)

    # Pass the data to a print-friendly template
    context = {
        "page_name": "valuation_print",
        "prospect": prospect,
        "evaluation_report": evaluation_report,
        "user": request.user
    }

    return render(request, 'valuations/EvaluationReportPrint.html', context=context)


@login_required
def printout_report(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)
    evaluation_report = get_object_or_404(VehicleEvaluationReport, prospect=prospect)

    # Pass the data to a print-friendly template
    context = {
        "page_name": "valuation_print",
        "prospect": prospect,
        "evaluation_report": evaluation_report,
        "user": request.user
    }

    return render(request, 'valuations/ValuationReport.html', context)


def get_all_prospect_data(request):
    companies = LoanCompany.objects.all()
    data = []  # Initialize an empty list to hold all prospects

    for company in companies:
        api_url_for_pending_prospects = f'{company.api}/prospects/?status=pending'
        api_url_for_payment_verified_prospects = f'{company.api}/prospects/?status=payment verified'

        try:
            print(f"Fetching data for company: {company.name}")
            
            # Fetch pending prospects
            pending_response = requests.get(api_url_for_pending_prospects)
            pending_response.raise_for_status()  # Raise an exception for HTTP errors
            pending_data = pending_response.json()

            # Fetch payment-verified prospects
            payment_verified_response = requests.get(api_url_for_payment_verified_prospects)
            payment_verified_response.raise_for_status()  # Raise an exception for HTTP errors
            payment_verified_data = payment_verified_response.json()

            # Append the fetched data to the main list
            data.extend(pending_data)
            data.extend(payment_verified_data)
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {company.name}: {e}")
            # Optionally, log or append error information for debugging

    # Render the data into the template
    context = {'prospects': data, "page_name": "valuation", "sub_page_name": ""}
    return render(request, 'prospects/all_prospect_jobs.html', context)


# API TO FETCH DATA FROM MABIS 
def fetch_prospects_from_mabis(request):
    # api_url = 'http://192.168.137.24:8000/api/prospects/?status=pending'
    api_url_pending = f"{request.user.active_company.api}/prospects/?status=pending"
    api_url_payment_verified = f"{request.user.active_company.api}/prospects/?status=payment verified"

    try:
        response = requests.get(api_url_pending)
        response.raise_for_status()
        payment_verified_response = requests.get(api_url_payment_verified)
        payment_verified_response.raise_for_status()
        data = response.json()
        data.extend(payment_verified_response.json())

        context = {'prospects': data, "page_name": "valuation", "sub_page_name": "payment_verification"}
        return render(request, 'valuations/pending_prospect.html', context)
    except requests.exceptions.RequestException as e:
        print('Error is this', e)
        return JsonResponse({'error': str(e)}, status=500)



# def fetch_vehicle_asset_for_prospect(request):
#     context = {'vehicle_data': VehicleAsset.objects.filter(), "page_name": "valuation", "sub_page_name": "asset_vehicle_list"}
#     return render(request, 'valuations/vehicle_listing.html', context)




def fetch_vehicle_asset_for_prospect(request):
    # Fetch all VehicleAsset records and their related VehicleEvaluationReport details
    vehicle_data = VehicleAsset.objects.prefetch_related(
        Prefetch(
            'vehicleevaluationreport_set',  # Reverse relation to VehicleEvaluationReport
            queryset=VehicleEvaluationReport.objects.only('make', 'model')
        )
    )

    context = {
        'vehicle_data': vehicle_data,
        "page_name": "valuation",
        "sub_page_name": "asset_vehicle_list"
    }
    return render(request, 'valuations/vehicle_listing.html', context)

def vehicle_detail_view(request, slug):
    # Fetch the vehicle by slug or return a 404 if not found
    vehicle = get_object_or_404(VehicleAsset, slug=slug)

    # Check for the existence of evaluation and inspection reports
    v_evaluation_reports = VehicleEvaluationReport.objects.filter(vehicle=vehicle).first()
    v_inspection_reports = VehicleInspectionReport.objects.filter(vehicle=vehicle).first()

    # Initialize context with default values
    context = {
        'vehicle': vehicle,
        'prospect': vehicle.prospect,
        "page_name": "valuation",
        "sub_page_name": "asset_vehicle_list",
    }

    # Add evaluation or inspection reports to the context if they exist
    if v_evaluation_reports:
        context['v_report'] = v_evaluation_reports

    if v_inspection_reports:
        context['inspection_report'] = v_inspection_reports

    # Render the template
    return render(request, 'valuations/vehicle_details.html', context)




# END OF VIEWS FOR HANDLING THE VALUATIONS SECTION FROM THE BASE.HTML
