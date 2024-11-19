from datetime import datetime
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField, Q
from django.contrib import messages
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
import json
from accounts.models import *
from prospects.models import *
from Valuation.models import *
import requests
from django.conf import settings


from api import serializers as ApiSerializers


# VIEWS FOR HANDLING THE PROSPECTS SECTION FROM THE BASE.HTML
# View to create a new prospect
class ProspectCreateView(LoginRequiredMixin, CreateView):
    model = Prospect
    form_class = ProspectCreateForm
    template_name = 'prospects/prospect_form.html'
    success_url = reverse_lazy('prospect_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Modify a field before saving
        form.instance.company = self.request.user.company
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter the agents field by the logged-in user's company and status Approved
        # form.fields['agent'].queryset = Agent.objects.filter(company=self.request.user.company, status='Approved', team_leader=self.request.user)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "prospects"
        context["sub_page_name"] = "create_prospects"
        return context



# view to list all currenltly available prospects
class ProspectListView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'prospects/prospect_list.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to exclude prospects with 'Pipeline' status
        # and order by 'New' status first, then by 'created_at'
        prospects =  Prospect.objects.exclude(status='Pipeline').annotate(
            is_new=Case(
                When(status='New', then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('is_new', '-updated_at').filter(agent__company=self.request.user.company)

        if "can_view_all_application_data" not in self.request.user.permissions:
            prospects = prospects.filter(created_by=self.request.user)
            # context["prospects"] = prospects
        return prospects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "prospects"
        context["sub_page_name"] =  "view_prospects"
        # context["prospects"] = "prospects"
        return context


#view prospects without any condition

# class ProspectListViewWithoutAgentCondition(LoginRequiredMixin, ListView):
#     model = Prospect
#     template_name = 'prospects/prospect_list.html'
#     context_object_name = 'prospects'

#     def get_queryset(self):
#         # Filter the queryset to exclude prospects with 'Pipeline' status
#         # and order by 'New' status first, then by 'created_at'
#         prospects =  Prospect.objects.exclude(status='Pipeline').annotate(
#             is_new=Case(
#                 When(status='New', then=Value(0)),
#                 default=Value(1),
#                 output_field=IntegerField(),
#             )
#         ).order_by('is_new', '-updated_at')

#         if "can_view_all_prospects_without_condition" in self.request.user.permissions:
#             prospects = Prospect.objects.get(all)
#             # context["prospects"] = prospects

#             #can_view_all_prospects_without_condition
#         return prospects

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["page_name"] =  "prospects"
#         context["sub_page_name"] =  "view_prospects"
#         # context["prospects"] = "prospects"
#         return context


# view for displaying details for a prospect
class ProspectDetailView(LoginRequiredMixin, View):
    model = Prospect
    template_name = 'valuations/prospect_detail.html'
    context_object_name = 'prospect'
    lookup_value = "slug"

    def get(self, request, slug):
        context = {}
        
        # fetch prospect
        try:
            api_url = f'{request.user.active_company.api}/prospects/{slug}'
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()
            # data.pop('id', None)
            
            print('\n\n\n Data',data)

            if data["valuation_submitted_by"]:
                data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk
            
            if data["valuation_reviewd_by"]:
                data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk
            
                
            if Prospect.objects.filter(slug = slug):
                # update saved record to track any changes
                prospect = Prospect.objects.filter(slug = slug).first()
                print('prospect pk',type(prospect.pk))
                print('prospect id',prospect.id)
                print('prospect name',prospect.name)
                serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)
                print('\n prospect serializer',serializer)
            else:
                data.pop('id', None)
                serializer = ApiSerializers.ProspectSerializer(data=data)

            if serializer.is_valid():
                prospect = serializer.save()    
                context['prospect'] = prospect
            else:

                print("\n", serializer.errors)

                
            # fetch vechicle assets
                
            api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
            response = requests.get(api_url)
            response.raise_for_status()
            v_data = response.json()
            for vehicle in v_data:
                vehicle['prospect'] = prospect.id
            print('\n\n\n\n v_data ' ,v_data)

            for vehicle_data in v_data:
                vehicle = VehicleAsset.objects.filter(slug = vehicle_data["slug"])
                # print('\n\n\n\n\n',vehicle)
                if not vehicle:
                    vehicle_data.pop('id', None)
                    vehicleSerializer = ApiSerializers.VehicleAssetSerializer(data=vehicle_data)
                    print('\n vehicleserializer',vehicleSerializer)
                    # print('\n\n\n\n\n',vehicleSerializer, '\n\n\n\n\n')
                   
                else:
                    vehicleSerializer = ApiSerializers.VehicleAssetSerializer(vehicle.first(), data=vehicle_data, partial=True)
                    print('\n\n vehicleserializer',vehicleSerializer)
                
            
                if vehicleSerializer.is_valid(raise_exception=True):
                    vehicleSerializer.save()
                        
                else:
                    print('\n\n',vehicleSerializer.errors)
                    

            vehicle_assets = VehicleAsset.objects.filter(prospect=prospect)
            if vehicle_assets:
                context['vehicle_asset_form'] = VehicleAssetForm(instance=vehicle_assets.first())
            else:
                context['vehicle_asset_form'] = VehicleAssetForm()

            context['vehicle_assets'] = vehicle_assets

            # implement for land assets

            # forms for modal

            context["page_name"] =  "valuation"
            context["sub_page_name"] =  "valuation_requests"
        
            return render(request, self.template_name, context=context)

                
        except requests.exceptions.RequestException as e:
            print('Error is this', e)
            return JsonResponse({'error': str(e)}, status=500)


    def post(self, request, *args, **kwargs):
        context = {}
        
        # fetch prospect
        api_url = f'{request.user.active_company.api}/prospects/{slug}'
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            prospect = response.json()

            context['prospect'] = prospect
        except:
            pass

        # save vehicle asset if available
        if request.POST.get("license_plate"):
            vehicle_asset = VehicleAsset.objects.filter(prospect=prospect)
            if not vehicle_asset:
                # no record
                vehicle_form = VehicleAssetForm(request.POST, request.FILES)
                if vehicle_form.is_valid():
                    v_asset = vehicle_form.save()
                    v_asset.prospect = prospect
                    v_asset.license_plate = v_asset.license_plate.upper()
                    v_asset.save()
                    prospect.status = 'Pending'
                    prospect.asset_submitted_on = datetime.now()
                    prospect.asset_submitted_by = request.user
                    prospect.save()
                    messages.add_message(request, messages.SUCCESS, "Submitted for Payment verification")
                else:
                    messages.add_message(request, messages.ERROR, "Error Creating Vehicle Record. Try Again.")
            else:
                # update old record
                vehicle_form = VehicleAssetForm(request.POST, request.FILES, instance=vehicle_asset.first())
                if vehicle_form.is_valid():
                    vehicle_form.save()
                    prospect.status = 'Pending'
                    prospect.asset_submitted_on = datetime.now()
                    prospect.asset_submitted_by = request.user
                    prospect.save()
                    messages.add_message(request, messages.SUCCESS, "Submitted for Payment verification")
                else:
                    messages.add_message(request, messages.ERROR, "Error Modifying Vehicle Records. Try Again")


        # save land asset if available
        if request.POST.get("land_location"):
            land_asset = LandAsset.objects.filter(prospect=prospect)
            if not land_asset:
                # no record
                land_form = LandAssetForm(request.POST, request.FILES)
                if land_form.is_valid():
                    l_asset = land_form.save()
                    l_asset.prospect = prospect
                    l_asset.save()
                    prospect.status = 'Pending'
                    prospect.asset_submitted_on = datetime.now()
                    prospect.asset_submitted_by = request.user
                    prospect.save()
                    messages.add_message(request, messages.SUCCESS, "Submitted for Payment verification")
                else:
                    messages.add_message(request, messages.ERROR, "Error Creating Land Record. Try Again")
            else:
                # update old record
                land_form = LandAssetForm(request.POST, request.FILES, instance=land_asset.first())
                if land_form.is_valid():
                    land_form.save()
                    prospect.status = 'Pending'
                    prospect.asset_submitted_on = datetime.now()
                    prospect.asset_submitted_by = request.user
                    prospect.save()

                    if request.GET.get("action") == "revaluation_request":
                        for loan_app in LoanApplication.objects.filter(prospect = prospect):
                            loan_app.delete()
                            
                    messages.add_message(request, messages.SUCCESS, "Submitted for Payment verification")
                else:
                    messages.add_message(request, messages.ERROR, "Error Modifying Land Records. Try Again")

        return redirect(reverse_lazy("prospect_list"))

# View to display prospects with 'Pending' status
class ProspectPendingView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'prospects/pending_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Pending' status
        return Prospect.objects.filter(status='Pending').order_by('-updated_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "prospects"
        context["sub_page_name"] =  "pending_valuation_prospects"
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "prospects"
        context["sub_page_name"] =  "pending_valuation_prospects"
        return context


# View to display prospects with 'Declined' status
class ProspectDeclinedView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'prospects/declined_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Declined' status
        return Prospect.objects.filter(status='Declined').order_by('updated_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "prospects"
        context["sub_page_name"] =  "declined_valuation_prospects"
        return context



#Restore  PROSPECT

class ProspectRestoreFromDecline(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        prospect = get_object_or_404(Prospect, slug=slug)
        prospect.status = 'Pending'
        prospect.save()
        return redirect(reverse('prospect_list'))


class ProspectRestoreFromFailed(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        prospect = get_object_or_404(Prospect, slug=slug)
        prospect.status = 'New'
        prospect.save()
        return redirect(reverse('prospect_list'))





# View to display prospects with 'Failed' status
class ProspectFailedView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'prospects/failed_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Failed' status
        return Prospect.objects.filter(status='Failed').order_by('updated_at').filter(agent__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "prospects"
        context["sub_page_name"] =  "Failed_prospects"
        return context

# END OF VIEWS FOR HANDLING THE PROSPECTS SECTION FROM THE BASE.HTML



# START OF VIEWS FOR HANDLING THE VALUATIONS SECTION FROM THE BASE.HTML
# View to list all prospects for.meant to enable accessing the prospect details where buttons for handling prospects with different
#  statuses from Pending to Review
class ValuationProspectListView(LoginRequiredMixin, View):
    model = Prospect
    template_name = 'valuations/prospect_list_valuation.html'
    context_object_name = 'prospects'
    context = {}

    def get(self, request):

        # api_url = 'http://192.168.20.83:8000/api/prospects/?status=valuation'
        api_url = f'{request.user.active_company.api}/prospects/?status=valuation'

        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            self.context['prospects'] = data
        except requests.exceptions.RequestException as e:
            messages.error(request, "Unable to fetch prospects")

        self.context["page_name"] =  "valuation"
        self.context["sub_page_name"] =  "valuation_requests"
        return render(request, 'valuations/pending_prospect.html', context=self.context)

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

    def get(self, request, slug):
        context = {}
        
        # fetch prospect
        try:
            api_url = f'{request.user.active_company.api}/prospects/{slug}'
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()
            if data["valuation_submitted_by"]:
                data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk
            
            if data["valuation_reviewd_by"]:
                data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk
            
                
            if Prospect.objects.filter(slug = slug):
                # update saved record to track any changes
                prospect = Prospect.objects.filter(slug = slug).first()
                serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)
            else:
                serializer = ApiSerializers.ProspectSerializer(data=data)

            if serializer.is_valid():
                prospect = serializer.save()    
                context['prospect'] = prospect
            else:

                print("\n\n\n", serializer.errors)

                # fetch vechicle assets
                
            api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
            response = requests.get(api_url)
            response.raise_for_status()
            v_data = response.json()

            for vehicle_data in v_data:
                vehicle = VehicleAsset.objects.filter(slug = vehicle_data["slug"])
                if not vehicle:
                    vehicleSerializer = ApiSerializers.VehicleAssetSerializer(data=vehicle_data)
                else:
                    vehicleSerializer = ApiSerializers.VehicleAssetSerializer(vehicle.first(), data=vehicle_data, partial=True)

                if vehicleSerializer.is_valid(raise_exception=True):
                    vehicleSerializer.save()


            vehicle_assets = VehicleAsset.objects.filter(prospect=prospect)
            if vehicle_assets:
                context['vehicle_asset_form'] = VehicleAssetForm(instance=vehicle_assets.first())


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
                context["valuers"] =  users_with_permission
            else:
                context['vehicle_asset_form'] = VehicleAssetForm()

            context['vehicle_assets'] = vehicle_assets

            # implement for land assets

            # forms for modal

            context["page_name"] =  "valuation"
            context["sub_page_name"] =  "valuation_review"
        
            return render(request, self.template_name, context=context)

                
        except requests.exceptions.RequestException as e:
            print('Error is this', e)
            return JsonResponse({'error': str(e)}, status=500)
        
    def post(self, request, *args, **kwargs):
        prospect = self.get_object()
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
    template_name = 'valuations/prospect_list_valuation.html'
    context_object_name = 'prospects'
    context = {}

    def get(self, request):

        api_url = f'{request.user.active_company.api}/prospects/?status=valuation'
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            self.context['prospects'] = data
        except requests.exceptions.RequestException as e:
            messages.error(request, "Unable to fetch prospects")

        self.context["page_name"] =  "valuation"
        self.context["sub_page_name"] =  "valuation_requests"
        return render(request, 'valuations/prospect_list_valuation.html', context=self.context)




# View for displaying prospects with 'Review' status
class ProspectReviewView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/review_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Failed' status
        return Prospect.objects.filter(status='Review').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "valuation_review"
        return context



# View for displaying prospects with 'Valuation Supervisor' status
class ProspectSupervisorReviewView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/supervisor_valuation_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Failed' status
        return Prospect.objects.filter(status='Valuation Supervisor').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] =  "valuation"
        context["sub_page_name"] =  "supevisor_valuation_requests"
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


# def DeclineView(request, slug):
#     prospect = get_object_or_404(Prospect, slug=slug)
#     prospect.status='Declined'
#     prospect.save()

#     context = {
#         "page_name": "valuation",
#         'prospect': prospect,
#         "sub_page_name" : "declined_valuation_prospects"
#     }

#     return render(request, 'prospects/prospect_list.html', context=context)

# @login_required
# def prospect_in_valuation(request, slug):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         payment_id = data.get('payment_id')
        
#         if not payment_id:
#             return JsonResponse({'error': 'No payment ID provided.'}, status=403)

#         prospect = Prospect.objects.filter(slug=slug, proof_of_payment_id=payment_id).first()
        
#         if not prospect:
#             return JsonResponse({'error': 'Invalid payment ID.'}, status=403)
        
#         # Update prospect's status and assign valuer
#         prospect.status = "Payment Verified"
#         prospect.payment_verified_on = timezone.now()
#         prospect.payment_verified_by = request.user
#         prospect.save()

#         # Get valuer assignment logic
#         users_with_permission = User.objects.filter(
#             role__permissions__code='can_be_valuers',
#             active_company=request.user.company
#         )
#         assignments = Prospect.objects.filter(valuer_assigned__in=users_with_permission).values('valuer_assigned').annotate(count=Count('valuer_assigned')).order_by('count')

#         if assignments:
#             # Get the valuer with the least assignments
#             least_assigned_valuer_id = assignments[0]['valuer_assigned']
#             valuer = User.objects.get(id=least_assigned_valuer_id)
#         else:
#             # If no assignments, return the first valuer
#             valuer = users_with_permission.first()
        
#         # Assign the valuer to the prospect
#         prospect.valuer_assigned = valuer
#         prospect.valuer_assigned_on = timezone.now()
#         prospect.save()

#         return JsonResponse({'success': 'Payment verified and valuer assigned.'})

#     return JsonResponse({'error': 'Invalid request method.'}, status=405)

# check two
# from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from .models import Prospect
import json

# @login_required
# def prospect_in_valuation(request, slug):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         payment_id = data.get('payment_id')
        
#         if not payment_id:
#             return JsonResponse({'error': 'No payment ID provided.'}, status=403)

#         # Fetch the prospect using slug and payment ID
#         prospect = Prospect.objects.filter(slug=slug, proof_of_payment_id=payment_id).first()
        
#         if not prospect:
#             return JsonResponse({'error': 'Invalid payment ID.'}, status=403)
        
#         # Update prospect's status and payment verification details
#         prospect.status = "Payment Verified"
#         prospect.payment_verified_on = timezone.now()
#         prospect.payment_verified_by = request.user
#         prospect.save()

#         # Fetch users with 'can_be_valuers' permission and count assigned prospects
#         users_with_permission = User.objects.filter(
#             role__permissions__code='can_be_valuers',
#             active_company=request.user.company
#         ).annotate(
#             assigned_count=Count('prospect', filter=Q(prospect__valuer_assigned=F('id')))
#         ).order_by('assigned_count', 'id')  # Order by count, then by ID to resolve ties

#         # Select the valuer with the least assignments
#         if users_with_permission.exists():
#             valuer = users_with_permission.first()
#         else:
#             return JsonResponse({'error': 'No valuers available for assignment.'}, status=403)

#         # Assign the valuer to the prospect and save
#         prospect.valuer_assigned = valuer
#         prospect.valuer_assigned_on = timezone.now()
#         prospect.save()

#         return JsonResponse({'success': 'Payment verified and valuer assigned.'})

#     return JsonResponse({'error': 'Invalid request method.'}, status=405)

#   FIRST PROSPECT IN VALUATION DETAILS VIEW
# @login_required
# def prospect_in_valuation(request, slug):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         payment_id = data.get('payment_id')
        
#         if not payment_id:
#             return JsonResponse({'error': 'No payment ID provided.'}, status=403)

#         # Fetch the prospect using slug and payment ID
#         prospect = Prospect.objects.filter(slug=slug, proof_of_payment_id=payment_id).first()
        
#         if not prospect:
#             return JsonResponse({'error': 'Invalid payment ID.'}, status=403)
        
#         # Update prospect's status and payment verification details
#         prospect.status = "Payment Verified"
#         prospect.payment_verified_on = timezone.now()
#         prospect.payment_verified_by = request.user
#         prospect.save()

#         # Fetch users with 'can_be_valuers' permission and count assigned prospects
#         valuers = User.objects.filter(
#             role__permissions__code='can_be_valuers',
#             active_company=request.user.company
#         )

#         assignments = Prospect.objects.values("valuer_assigned").annotate(count=Count('id'))
#         if assignments:
#             if len(assignments) == len(valuers):
#                 prospect.valuer_assigned = valuers[0]
#                 prospect.valuer_assigned_on = timezone.now()
#                 prospect.save()

#             else:
#                 for valuer in valuers:
#                     # if relation_officer.pk not in [assignment["relation_officer"] for assignment in assignments]:
#                     if valuer.pk not in [assignment['valuer_assigned'] for assignment in assignments]:
#                         prospect.valuer_assigned = valuer
#                         prospect.valuer_assigned_on = timezone.now()
#                         prospect.save()
#                         return redirect('view-pipeline')
                    
#                 # already_assigned
#                 min_assignment = assignments[0]
#                 for assignment in assignments:
#                     if assignment["count"] < min_assignment["count"]:
#                         min_assignment = assignment

#                 if User.objects.filter(pk=min_assignment["valuer_assigned"]):
#                     prospect.valuer_assigned = User.objects.filter(pk=min_assignment["valuer_assigned"]).first()
#                     prospect.valuer_assigned_on = timezone.now()
#                     prospect.save()
#         else:
#             if valuers:
#                 prospect.valuer_assigned = valuers[0]
#                 prospect.valuer_assigned_on = timezone.now()
#                 prospect.save()


#         return JsonResponse({'success': 'Payment verified and valuer assigned.'})

#     return JsonResponse({'error': 'Invalid request method.'}, status=405)

# View to handle setting prospect status to Valuation
# @login_required
# def prospect_in_valuation(request, slug):
#     prospect = get_object_or_404(Prospect, slug=slug)

#     # Change the status to 'Valuation'
#     prospect.status = 'Valuation'
#     prospect.submitted_for_valuation_on = datetime.now()
#     prospect.submitted_for_valuation_by = request.user
#     prospect.save()  # Save the updated prospect instance to the database

#     # Redirect back to the previous page
#     # return redirect(request.META.get('HTTP_REFERER', 'default-url'))
#     # return redirect('valuation_prospect_detail', pk=prospect.id)  # Use 'default-url' if HTTP_REFERER is not available
#     return redirect('prospect_valuation')

from django.db.models import Count, Q
# @login_required
# def prospect_in_valuation(request, slug):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         payment_id = data.get('payment_id', None)
#         if not payment_id:
#             return HttpResponse(status_code=403)

#         # confirm trans_id is matching
#         prospect = Prospect.objects.filter(slug=slug, proof_of_payment_id=payment_id)
#         if not prospect:
#             return HttpResponse(status_code=403)

#         prospect = prospect.first()
#         prospect.status = "Payment Verified"
#         prospect.payment_verified_on = datetime.now()
#         prospect.payment_verified_by = request.user
    
#         prospect.save()

#         users_with_permission = User.objects.filter(
#             # role__permissions__code='can_view_valuation_requests',
#             role__permissions__code='can_be_valuers',
#             active_company=request.user.company
#         )
#         # assignments = Prospect.objects.values("submitted_for_valuation_by").annotate(count=Count('id'))
#         assignments = Prospect.objects.values("valuer_assigned").annotate(count=Count('id'))

#         if assignments:
#             if len(assignments) == len(users_with_permission):
                
#                 # prospect.submitted_for_valuation_by = users_with_permission[0]
#                 # prospect.submitted_for_valuation_on = datetime.now()
#                 prospect.valuer_assigned = users_with_permission[0]
#                 prospect.valuer_assigned_on = datetime.now()
#                 prospect.save()
#             else:
#                 for valuer in users_with_permission:
#                     if valuer.id not in [assignment['submitted_for_valuation_by'] for assignment in assignments]:
#                         # prospect.submitted_for_valuation_by = valuer
#                         # prospect.submitted_for_valuation_on = datetime.now()
#                         prospect.valuer_assigned = users_with_permission[0]
#                         prospect.valuer_assigned_on = datetime.now()
#                         prospect.save()
#                         break

#         return redirect(reverse('valuation_prospect_detail', kwargs={'slug': prospect.slug}))


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
        data = json.loads(request.body)
        payment_id = data.get('payment_id', None)
        if not payment_id:
            return JsonResponse({'error': 'No payment ID provided.'}, status=403)
        

        api_url = f'{request.user.active_company.api}/prospects/{slug}/'
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            prospect = response.json()
        except:
            return JsonResponse({'error': 'Invalid payment ID.'}, status=403)

        # Retrieve the single prospect to verify and assign

        if not prospect:
            return JsonResponse({'error': 'Invalid payment ID.'}, status=403)

        # Update prospect's status to "Payment Verified"
        
        api_url = f'{request.user.active_company.api}/prospects/{slug}/'
        try:
            # assign valuer

            users_with_permission = User.objects.filter(
                # role__permissions__code='can_view_valuation_requests',
                role__permissions__code='can_be_valuers',
                active_company=request.user.company
            )

            # Get all prospects with an assigned valuer
            valuer_assignments = (
                Prospect.objects
                .exclude(valuer_assigned=None)  # Exclude unassigned prospects
                .values('valuer_assigned')  # Group by each valuer
                .annotate(assign_count=Count('valuer_assigned'))  # Count their assignments
                .order_by('assign_count')  # Sort by the count in ascending order
            )

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
                response = requests.patch(api_url, data={
                    "status" : "Payment Verified",
                    "payment_verified_on" : datetime.now(),
                    "payment_verified_by" : request.user.username,
                    "valuer_assigned" : least_assigned_valuer.name,
                    "valuer_assigned_on" : timezone.now(),
                })
                if response.status_code >= 200 and response.status_code <= 399:
                    # was successful
                    return JsonResponse({'success': 'Payment verified and valuer assigned.'})
                else:
                    return JsonResponse({'error': 'Unable to update prospect data'}, status=403)
            else:
                return JsonResponse({'error': 'No valuers available.'}, status=404)
        except Exception as err:
            return JsonResponse({'error': 'Invalid payment ID.'}, status=403)

        # Retrieve all users with 'can_be_valuers' permission in the user's active company

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
    api_url = f'{request.user.active_company.api}/prospects/{slug}/'
    
    response = requests.patch(api_url, data={
        "submitted_for_valuation_by" : request.user.username,
        "submitted_for_valuation_on" : datetime.now(),
        "status" : 'Valuation'
    })
    if response.status_code >= 200 and response.status_code <= 399:
        # was successful
        return redirect('prospect_valuation')
    else:
        return redirect(reverse_lazy("prospect_detail", args=[slug]))


# View for adding evaluation report details for a particular prospect
@login_required
def add_valuation_report_details(request, slug):

    api_url = f'{request.user.active_company.api}/prospects/{slug}/'
    if Prospect.objects.filter(slug=slug):
        prospect = Prospect.objects.filter(slug=slug).first()
    else:
        # fetch and save prospect
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        if data["valuation_submitted_by"]:
            data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk
        
        if data["valuation_reviewd_by"]:
            data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk

        data = response.json()
        if data["valuation_submitted_by"]:
            data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk
        
        if data["valuation_reviewd_by"]:
            data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk
            
        if Prospect.objects.filter(slug = slug):
            # update saved record to track any changes
            prospect = Prospect.objects.filter(slug = slug).first()
            serializer = ApiSerializers.ProspectSerializer(prospect, data=response.json(), partial=True)
        else:
            serializer = ApiSerializers.ProspectSerializer(data=response.json())

        if serializer.is_valid():
            prospect = serializer.save()

        
    if not prospect:
        messages.error("Prospec no found")
        return redirect("prospect_valuation")

    context = {
        "page_name": "valuation",
        'prospect': prospect,
        "sub_page_name" : "declined_valuation_prospects"
    }

    if request.method == 'POST':
        prospect = Prospect.objects.filter(slug=slug).first()
        # Vehicles
        v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
        if not v_reports:
            form = VehicleEvaluationReportForm(request.POST, request.FILES, prospect=prospect)
            if form.is_valid():
                form = form.save(commit=False)
                form.prospect = prospect
                # prospect.status = 'Valuation Supervisor'
                
                form.save()

                # fields = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect).first()
                # fields = v_reports.first()
                # fields_data = {}
                # Save market_value and forced_sale to the fields JSONField as specified
                form.fields = {
                    "market_value": form.market_value,
                    "forced_sale": form.forced_sale
                }
                form.save()  # Now save the changes to the fields JSONField


                # update upstream prospect status
                response = requests.patch(api_url, data={
                    "status" : 'Valuation Supervisor',
                    "valuation_submitted_on" : datetime.now(),
                    "valuation_submitted_by" : request.user.username,
                })
                if response.status_code >= 200 and response.status_code <= 399:
                    prospect.status = 'Valuation Supervisor'
                    prospect.valuation_submitted_on = datetime.now()
                    prospect.valuation_submitted_by = request.user
                    prospect.save()

                # Redirect to the 'valuation_prospect_detail' page
                messages.add_message(request, messages.SUCCESS, "Asset Valuation submitted successfully")
                return redirect('valuation_prospect_detail', pk=prospect.id)
            else:
                messages.add_message(request, messages.ERROR, "ERROR MODIFYING RECORDS. TRY AGAIN!!")
        else:
            # save edited data
            submitted_report_id = request.GET.get("form_id")
            if submitted_report_id:
                report = VehicleEvaluationReport.objects.filter(pk=submitted_report_id)
                # save updated data
                if not report:
                    messages.add_message(request, messages.ERROR, "REPORT NOT FOUND. TRY AGAIN!")
                else:
                    form = VehicleEvaluationReportForm(request.POST, request.FILES, instance=report.first(), prospect=prospect)
                    if form.is_valid():
                        form = form.save(commit=False)
                        form.prospect = prospect
                        # form.prospect.status = 'Valuation Supervisor'
                        form.save()
                        # prospect.status = 'Review'

                        # update upstream prospect status
                        response = requests.patch(api_url, data={
                            "status" : prospect.status,
                            "valuation_submitted_on" : datetime.now(),
                            "valuation_submitted_by" : request.user.username,
                        })
                        if response.status_code >= 200 and response.status_code <= 399:
                            prospect.status = prospect.status
                            prospect.valuation_submitted_on = datetime.now()
                            prospect.valuation_submitted_by = request.user

                        messages.add_message(request, messages.SUCCESS, "RECORDS MODIFIED SUCCESSFULLY")

            # redirect to details page if form id is found or not
            return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

    else:
        prospect = Prospect.objects.filter(slug=slug).first()

        v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
        if v_reports:
            # prospect.status = 'Valuation Supervisor' --> don't put prospect status here.
            context["v_reports"] = [{"form": VehicleEvaluationReportForm(instance=report, prospect=prospect), "report": report, } for report in v_reports]
        else:
            context["create_vehicle_report_form"] = VehicleEvaluationReportForm(prospect=prospect)


    return render(request, 'valuations/evaluation_report_form.html', context=context)


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

    api_url = f'{request.user.active_company.api}/prospects/{slug}/'
    if Prospect.objects.filter(slug=slug):
        prospect = Prospect.objects.filter(slug=slug).first()
    else:
        # fetch and save prospect
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        if data["valuation_submitted_by"]:
            data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk
        
        if data["valuation_reviewd_by"]:
            data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk
            
        if Prospect.objects.filter(slug = slug):
            # update saved record to track any changes
            prospect = Prospect.objects.filter(slug = slug).first()
            serializer = ApiSerializers.ProspectSerializer(prospect, data=response.json(), partial=True)
        else:
            serializer = ApiSerializers.ProspectSerializer(data=response.json())

        if serializer.is_valid():
            prospect = serializer.save()

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
        response = requests.patch(api_url, data={
            "status" : 'Review',
            "valuation_submitted_on" : datetime.now(),
            "valuation_submitted_by" : request.user.username,
        })
        if response.status_code >= 200 and response.status_code <= 399:
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

# END OF VIEWS FOR HANDLING THE VALUATIONS SECTION FROM THE BASE.HTML




@login_required
def PipelineView(request, slug):
    # Get the prospect object
    prospect = get_object_or_404(Prospect, slug=slug)

    # Check if the request is a POST request to handle the form submission
    if request.method == 'POST':

        # check for vehicle or land valuation report
        v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
        l_reports = LandEvaluationReport.objects.filter(land__prospect=prospect)

        
        # if this prospect has a valuation report proceed
        if v_reports or l_reports:
            # submit reports to upstream
            for v_report in v_reports:
                serializer = ApiSerializers.VehicleEvaluationReportSerializer(v_report)

                api_url = f'{request.user.active_company.api}/vehicle-reports/'
                # handle images

                files = {
                    "right_hand_side_view": open(f"{settings.BASE_DIR}{serializer.data.get("right_hand_side_view")}", "rb"),
                    "left_hand_eside_view": open(f"{settings.BASE_DIR}{serializer.data.get("left_hand_eside_view")}", "rb"),
                    "engine_compartment": open(f"{settings.BASE_DIR}{serializer.data.get("engine_compartment")}", "rb"),
                    "upholstery": open(f"{settings.BASE_DIR}{serializer.data.get("upholstery")}", "rb"),
                    "vehicle_id_plate": open(f"{settings.BASE_DIR}{serializer.data.get("vehicle_id_plate")}", "rb"),
                }
                serializer.data.pop('right_hand_side_view', None)
                serializer.data.pop('left_hand_eside_view', None)
                serializer.data.pop('engine_compartment', None)
                serializer.data.pop('upholstery', None)
                serializer.data.pop('vehicle_id_plate', None)

                response = requests.post(api_url, data=serializer.data, files=files)

                if response.status_code >= 200 and response.status_code <= 399:

                    api_url = f'{request.user.active_company.api}/prospects/{slug}/'
                    response = requests.patch(api_url, data={
                        "status" : 'Pipeline',
                        "valuation_reviewd_on" : datetime.now(),
                        "valuation_reviewd_by" : request.user.username,
                    })

                    
                    if response.status_code >= 200 and response.status_code <= 399:
                        prospect.status = 'Pipeline'
                        prospect.valuation_reviewd_on = datetime.now()
                        prospect.valuation_reviewd_by = request.user
                        prospect.save()

            return redirect(reverse_lazy("prospect_review"))


        messages.add_message(request, messages.ERROR, "NO VALUATION REPORT FOUND FOR THIS PROSPECT!")
    return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))
# END OF VIEWS FOR HANDLING THE LOAN APPLICATION FROM THE BASE.HTML
