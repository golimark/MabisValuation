from datetime import datetime
from django.core.mail import EmailMessage
from time import sleep
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView

from prospects.tasks import send_email_task
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
from urllib.parse import urlparse


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
        if request.user.active_company:
            context = {}

            # fetch prospect
            try:
                api_url = f'{request.user.active_company.api}/prospects/{slug}'
                response = requests.get(api_url)
                response.raise_for_status()

                data = response.json()

                if data["valuation_submitted_by"]:
                    data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk # if User.objects.filter(username=data["valuation_submitted_by"]).first() else User.objects.filter(username=data["valuation_submitted_by"]).first()

                if data["valuation_reviewd_by"]:
                    data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk #if User.objects.filter(username=data["valuation_reviewd_by"]).first() else User.objects.filter(username=data["valuation_reviewd_by"]).first()

                if Prospect.objects.filter(slug = slug):
                    # update saved record to track any changes
                    prospect = Prospect.objects.filter(slug = slug).first()
                    serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)
                    context['prospect'] = prospect
                else:
                    serializer = ApiSerializers.ProspectSerializer(data=data)

                if serializer.is_valid():
                    parsed_url = urlparse(request.user.active_company.api)
                    port = parsed_url.port

                    # Modify the proof_of_payment URL to include the port number

                    # Modify the proof_of_payment URL to include the port number
                    validated_data = serializer.validated_data
                    if validated_data.get('proof_of_payment'):
                        # print(validated_data['proof_of_payment'])
                        if port:
                            proof_of_payment_url = urlparse(validated_data['proof_of_payment'])
                            proof_of_payment_url = proof_of_payment_url._replace(netloc=f"{proof_of_payment_url.hostname}:{port}")
                        else:
                            proof_of_payment_url = urlparse(validated_data['proof_of_payment'])
                        # proof_of_payment_url = proof_of_payment_url._replace(netloc=f"{proof_of_payment_url.hostname}:{port}")
                        validated_data['proof_of_payment'] = proof_of_payment_url.geturl()

                    prospect = serializer.save()

                    context['prospect'] = prospect

                # fetch vechicle assets
                api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
                response = requests.get(api_url)
                response.raise_for_status()
                v_data = response.json()
                for vehicle in v_data:
                    vehicle['prospect'] = context['prospect'].id

                for vehicle_data in v_data:
                    vehicle = VehicleAsset.objects.filter(slug = vehicle_data["slug"])

                    if not vehicle:
                        vehicleSerializer = ApiSerializers.VehicleAssetSerializer(data=vehicle_data)

                    else:
                        vehicleSerializer = ApiSerializers.VehicleAssetSerializer(vehicle.first(), data=vehicle_data, partial=True)


                    if vehicleSerializer.is_valid(raise_exception=True):
                        # first handle modifying the url to have  port number
                        parsed_url = urlparse(request.user.active_company.api)
                        port = parsed_url.port

                        validated_data = vehicleSerializer.validated_data
                        if validated_data.get('logbook'):
                        # print(validated_data['proof_of_payment'])
                            if port:
                                logbook_url = urlparse(validated_data['logbook'])
                                logbook_url = logbook_url._replace(netloc=f"{logbook_url.hostname}:{port}")
                            else:
                                logbook_url = urlparse(validated_data['logbook'])
                            # logbook_url = logbook_url._replace(netloc=f"{logbook_url.hostname}:{port}")
                            validated_data['logbook'] = logbook_url.geturl()

                        vehicleSerializer.save()

                users_with_permission = User.objects.filter(
                        role__permissions__code='can_be_valuers',
                        company=self.request.user.company
                    )
                context["valuers"] =  users_with_permission

                vehicle_assets = VehicleAsset.objects.filter(prospect=context['prospect'])
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
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')



    def post(self, request, *args, **kwargs):
        if request.user.active_company:
            prospect = get_object_or_404(Prospect, slug=kwargs['slug'])
            # api_url = f'{request.user.active_company.api}/vehicles/?prospect={self.slug}'

            valuer_id = request.POST.get("valuer")

            try:
                api_url = f'{request.user.active_company.api}/prospects/{prospect.slug}/'
                valuer = User.objects.get(
                    pk=valuer_id,
                    role__permissions__code='can_be_valuers',
                    company=request.user.company
                )
                print('\n\nvaluer.name before \n\n', valuer.name)
                # Explicitly concatenate first and last name to avoid property issues
                valuer_name = f"{valuer.first_name} {valuer.last_name}"

                print('\n\nvaluer.name after \n\n', valuer.name)

                if valuer:
                    print(f"Selected valuer: {valuer.name} (ID: {valuer.id})")
                    response = requests.patch(api_url, data={
                        "valuer_assigned" : valuer.name,
                        "valuer_assigned_on" : timezone.now(),
                    })
                    if response.status_code >= 200 and response.status_code <= 399:
                        # was successful
                        # Assign the valuer's name to the prospect field
                        prospect.valuer_assigned = valuer.name
                        prospect.valuer_assigned_on = timezone.now()
                        prospect.save()

                        messages.success(request, "Valuer assigned successfully.")
                        return redirect(reverse('valuation_prospect_detail', kwargs={'slug': prospect.slug}))
                    else:
                        return JsonResponse({'error': 'Unable to update prospect data'}, status=403)
                else:
                    return JsonResponse({'error': 'No valuers available.'}, status=404)

            except User.DoesNotExist:
                messages.error(request, "Selected valuer is invalid or does not have permission.")

            # Redirect back to the same page after processing
            return redirect(reverse('valuation_prospect_detail', kwargs={'slug': prospect.slug}))
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')

# view for displaying details for a prospect
class ProspectDetailViewforNewProspects(LoginRequiredMixin, View):
    model = Prospect
    template_name = 'valuations/prospect_detail.html'
    context_object_name = 'prospect'
    lookup_value = "slug"

    def get(self, request, slug):
        if request.user.active_company:
            context = {}

            # fetch prospect
            try:
                api_url = f'{request.user.active_company.api}/prospects/{slug}'
                response = requests.get(api_url)
                response.raise_for_status()

                data = response.json()
                print('\n\n got this data here', data)

                if data["valuation_submitted_by"]:
                    data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk if User.objects.filter(username=data["valuation_submitted_by"]).first() else User.objects.filter(username=data["valuation_submitted_by"]).first()

                if data["valuation_reviewd_by"]:
                    data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk if User.objects.filter(username=data["valuation_reviewd_by"]).first() else User.objects.filter(username=data["valuation_reviewd_by"]).first()


                if Prospect.objects.filter(slug = slug):
                    # update saved record to track any changes
                    prospect = Prospect.objects.filter(slug = slug).first()

                    serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)


                else:
                    serializer = ApiSerializers.ProspectSerializer(data=data)

                if serializer.is_valid():
                    parsed_url = urlparse(request.user.active_company.api)
                    port = parsed_url.port

                    # Modify the proof_of_payment URL to include the port number

                    # Modify the proof_of_payment URL to include the port number
                    validated_data = serializer.validated_data
                    if validated_data.get('proof_of_payment'):
                        # print(validated_data['proof_of_payment'])
                        proof_of_payment_url = urlparse(validated_data['proof_of_payment'])
                        proof_of_payment_url = proof_of_payment_url._replace(netloc=f"{proof_of_payment_url.hostname}:{port}")
                        validated_data['proof_of_payment'] = proof_of_payment_url.geturl()

                    prospect = serializer.save()

                    context['prospect'] = prospect

                else:
                    print(serializer.errors)
                # fetch vechicle assets

                api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
                response = requests.get(api_url)
                response.raise_for_status()
                v_data = response.json()
                for vehicle in v_data:
                    vehicle['prospect'] = prospect.id

                for vehicle_data in v_data:
                    vehicle = VehicleAsset.objects.filter(slug = vehicle_data["slug"])

                    if not vehicle:
                        vehicleSerializer = ApiSerializers.VehicleAssetSerializer(data=vehicle_data)

                    else:
                        vehicleSerializer = ApiSerializers.VehicleAssetSerializer(vehicle.first(), data=vehicle_data, partial=True)


                    if vehicleSerializer.is_valid(raise_exception=True):
                        # first handle modifying the url to have  port number
                        parsed_url = urlparse(request.user.active_company.api)
                        port = parsed_url.port

                        validated_data = vehicleSerializer.validated_data
                        if validated_data.get('logbook'):
                        # print(validated_data['proof_of_payment'])
                            logbook_url = urlparse(validated_data['logbook'])
                            logbook_url = logbook_url._replace(netloc=f"{logbook_url.hostname}:{port}")
                            validated_data['logbook'] = logbook_url.geturl()

                        vehicleSerializer.save()

                users_with_permission = User.objects.filter(
                        role__permissions__code='can_be_valuers',
                        company=self.request.user.company
                    )
                context["valuers"] =  users_with_permission

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
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')


    def post(self, request, *args, **kwargs):
        if request.user.active_company:

            # print('\n\n\n at point of posting')
            # if 'valuer.id' in request.POST:

            # prospect = Prospect.objects.get(slug=kwargs['slug']).first()
            prospect = get_object_or_404(Prospect, slug=kwargs['slug'])
            print('\n\n prospect', prospect)
            # print("\n\n\n\n prospect",prospect)
            valuer_id = request.POST.get("valuer")

            try:
                valuer = User.objects.get(
                    id=valuer_id,
                    role__permissions__code='can_be_valuers',
                    company=request.user.company
                )
                # Assign the valuer to the prospect and save
                prospect.valuer_assigned = valuer.username
                prospect.valuer_assigned_on = timezone.now()
                prospect.save()
                messages.success(request, "Valuer assigned successfully.")
                return redirect(reverse('valuation_prospect_detail_new_prospect', kwargs={'slug': prospect.slug}))
            except User.DoesNotExist:
                messages.error(request, "Selected valuer is invalid or does not have permission.")

            # Redirect back to the same page after processing
            return redirect(reverse('valuation_prospect_detail_new_prospect', kwargs={'slug': prospect.slug}))
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')




# View to display prospects with 'Pending' status
class ProspectPendingView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'prospects/pending_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Pending' status
        return Prospect.objects.filter(Q(status='Pending')|Q(status='Payment Verified')).order_by('-updated_at').filter(company=self.request.user.company)

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
        if request.user.active_company:

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
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')

# view for showing prospects with 'Pending' status to enable access to customized buttons
class ValuationProspectPendingView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/pending_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Pending' status
        return Prospect.objects.filter(status='Pending').order_by('created_at').filter(company=self.request.user.company)

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
        if request.user.active_company:

            context = {}

            # fetch prospect
            try:
                api_url = f'{request.user.active_company.api}/prospects/{slug}'
                response = requests.get(api_url)
                response.raise_for_status()

                data = response.json()

                if data["valuation_submitted_by"]:
                    data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first().pk if User.objects.filter(username=data["valuation_submitted_by"]).first() else User.objects.filter(username=data["valuation_submitted_by"]).first()

                if data["valuation_reviewd_by"]:
                    data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first().pk if User.objects.filter(username=data["valuation_reviewd_by"]).first() else User.objects.filter(username=data["valuation_reviewd_by"]).first()


                if Prospect.objects.filter(slug = slug):
                    # update saved record to track any changes
                    prospect = Prospect.objects.filter(slug = slug).first()
                    serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)
                else:
                    serializer = ApiSerializers.ProspectSerializer(data=data)

                if serializer.is_valid():
                    prospect = serializer.save()
                    context['prospect'] = prospect


                # fetch vechicle assets

                api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
                response = requests.get(api_url)
                response.raise_for_status()
                v_data = response.json()

                for vehicle in v_data:
                    vehicle['prospect'] = prospect.id

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
                    context['v_evaluation_reports'] = VehicleEvaluationReport.objects.filter(vehicle__in=vehicle_assets).order_by('-created_at')

                    # for inspection report
                    context['inspection_reports'] = VehicleInspectionReport.objects.filter(vehicle__in=vehicle_assets)


                    # land asset
                    land_assets = LandAsset.objects.filter(prospect=prospect)
                    if land_assets:
                        context['land_asset'] = land_assets

                    users_with_permission = User.objects.filter(
                        role__permissions__code='can_be_valuers',
                        company=self.request.user.company
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
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')

    def post(self, request, slug):
        if request.user.active_company:

            valuer_id = request.POST.get("valuer")

            api_url = f'{request.user.active_company.api}/prospects/{slug}/'
            response = requests.get(api_url)
            response.raise_for_status()
            prospect = response.json()

            if prospect:
                try:
                    valuer = User.objects.get(
                        id=valuer_id,
                        role__permissions__code='can_be_valuers',
                        company=request.user.company
                    )
                    # Assign the valuer to the prospect and save
                    prospect['valuer_assigned'] = valuer.username
                    prospect['valuer_assigned_on'] = timezone.now()
                    # prospect.save()

                    response = requests.patch(api_url, data={
                            "status" : "Payment Verified",
                            "payment_verified_on" : datetime.now(),
                            "payment_verified_by" : request.user.username,
                            "valuer_assigned" : prospect['valuer_assigned'],
                            "valuer_assigned_on" : timezone.now(),
                        })

                    if response.status_code >= 200 and response.status_code <= 399:
                        print('Response is: ',response.status_code)
                        # was successful
                        messages.success(request, "Valuer assigned successfully.")
                        # return JsonResponse({'success': 'Payment verified and valuer assigned.'})
                        return redirect(reverse('valuation_prospect_detail', args=[slug]))

                except User.DoesNotExist:
                    messages.error(request, "Selected valuer is invalid or does not have permission.")

                # Redirect back to the same page after processing
                return redirect(reverse('valuation_prospect_detail', args=[slug]))
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')




# view for displaying details for a prospect with accessibility to customized buttons
class ValuationProspectDetailViewforNewProspects(LoginRequiredMixin, DetailView):
    model = Prospect
    template_name = 'valuations/prospect_detail.html'
    context_object_name = 'prospect'
    lookup_value = "slug"

    def get(self, request, slug):
        if request.user.active_company:

            context = {}

            # fetch prospect
            try:
                api_url = f'{request.user.active_company.api}/prospects/{slug}'
                response = requests.get(api_url)
                response.raise_for_status()

                data = response.json()

                if data["valuation_submitted_by"]:
                    data["valuation_submitted_by"] = User.objects.filter(username=data["valuation_submitted_by"]).first()

                if data["valuation_reviewd_by"]:
                    data["valuation_reviewd_by"] = User.objects.filter(username=data["valuation_reviewd_by"]).first()


                if Prospect.objects.filter(slug = slug):
                    # update saved record to track any changes
                    prospect = Prospect.objects.filter(slug = slug).first()
                    serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)
                else:
                    serializer = ApiSerializers.ProspectSerializer(data=data)

                if serializer.is_valid():
                    prospect = serializer.save()
                    context['prospect'] = prospect


                # fetch vechicle assets

                api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
                response = requests.get(api_url)
                response.raise_for_status()
                v_data = response.json()

                for vehicle in v_data:
                    vehicle['prospect'] = prospect.id

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

                    # for inspection report
                    context['inspection_reports'] = VehicleInspectionReport.objects.filter(vehicle__in=vehicle_assets)


                    # land asset
                    land_assets = LandAsset.objects.filter(prospect=prospect)
                    if land_assets:
                        context['land_asset'] = land_assets

                    users_with_permission = User.objects.filter(
                        role__permissions__code='can_be_valuers',
                        company=self.request.user.company
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
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')

    def post(self, request, slug):
        if request.user.active_company:
            # print('\n\n\n at point of posting')
            valuer_id = request.POST.get("valuer")

            api_url = f'{request.user.active_company.api}/prospects/{slug}/'
            response = requests.get(api_url)
            response.raise_for_status()
            prospect = response.json()

            if prospect:
                try:
                    valuer = User.objects.get(
                        id=valuer_id,
                        role__permissions__code='can_be_valuers',
                        company=request.user.company
                    )
                    # Assign the valuer to the prospect and save
                    prospect['valuer_assigned'] = valuer.username
                    prospect['valuer_assigned_on'] = timezone.now()
                    # prospect.save()

                    response = requests.patch(api_url, data={
                            "status" : "Payment Verified",
                            "payment_verified_on" : datetime.now(),
                            "payment_verified_by" : request.user.username,
                            "valuer_assigned" : prospect['valuer_assigned'],
                            "valuer_assigned_on" : timezone.now(),
                        })

                    if response.status_code >= 200 and response.status_code <= 399:
                        print('Response is: ',response.status_code)
                        # was successful
                        messages.success(request, "Valuer assigned successfully.")
                        # return JsonResponse({'success': 'Payment verified and valuer assigned.'})
                        return redirect(reverse('valuation_prospect_detail_new_prospect', args=[slug]))

                except User.DoesNotExist:
                    messages.error(request, "Selected valuer is invalid or does not have permission.")

                # Redirect back to the same page after processing
                return redirect(reverse('valuation_prospect_detail_new_prospect', args=[slug]))
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')




# View to display prospects with 'Valuation' status
class ProspectValuationView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/prospect_list_valuation.html'
    context_object_name = 'prospects'

    def get(self, request):
        if request.user.active_company:
            context = {}
            api_url = f'{request.user.active_company.api}/prospects/?status=valuation'
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                context['prospects'] = data

                if 'can_verify_payment' in request.user.permissions:
                    context['prospects'] = [prospect for prospect in context['prospects']]
                else:
                    context['prospects'] = [prospect for prospect in context['prospects'] if (prospect['valuer_assigned'] == request.user.username or prospect['valuer_assigned'] == (request.user.first_name + ' ' + request.user.last_name))]

                # valuer_assigned = request.GET.get('valuer_assigned')
                # if valuer_assigned:
                if 'can_verify_payment' in request.user.permissions:
                    context['prospects'] = [prospect for prospect in context['prospects']]
                else:
                    context['prospects'] = [prospect for prospect in data if (prospect['valuer_assigned'] == request.user.username or prospect['valuer_assigned'] == (request.user.first_name + ' ' + request.user.last_name))]

            except requests.exceptions.RequestException:
                messages.error(request, "Unable to fetch prospects")

            context["page_name"] =  "valuation"
            context["sub_page_name"] =  "valuation_requests"
            return render(request, 'valuations/prospect_list_valuation.html', context=context)

        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')

# class ProspectValuationView(LoginRequiredMixin, ListView):
#     model = Prospect
#     template_name = 'valuations/prospect_list_valuation.html'
#     context_object_name = 'prospects'
#     context = {}

#     def get(self, request):

#         api_url = f'{request.user.active_company.api}/prospects/?status=valuation'
#         try:
#             response = requests.get(api_url)
#             response.raise_for_status()
#             data = response.json()
#             self.context['prospects'] = data
#         except requests.exceptions.RequestException as e:
#             messages.error(request, "Unable to fetch prospects")

#         self.context["page_name"] =  "valuation"
#         self.context["sub_page_name"] =  "valuation_requests"
#         return render(request, 'valuations/prospect_list_valuation.html', context=self.context)

# View to display prospects with 'Valuation' status
class InspectionView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/inspection_list.html'
    context_object_name = 'prospects'

    def get(self, request):
        if request.user.active_company:
            context = {}
            api_url = f'{request.user.active_company.api}/prospects/?status=inspection'
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                print('\n\n\n data', data)
                context['prospects'] = data
            except requests.exceptions.RequestException:
                messages.error(request, "Unable to fetch prospects")

            # valuer_assigned = request.GET.get('valuer_assigned')
            # if valuer_assigned:
            #     context['prospects'] = [prospect for prospect in context['prospects'] if prospect['valuer_assigned'] == valuer_assigned]

            context["page_name"] =  "valuation"
            context["sub_page_name"] =  "inspection_requests"
            return render(request, 'valuations/inspection_list.html', context=context)
        else:
            messages.error(request, "Please select a loan company to work with before you proceed.")
            return redirect('dashboard')



# View for displaying prospects with 'Review' status
class ProspectReviewView(LoginRequiredMixin, ListView):
    model = Prospect
    template_name = 'valuations/review_prospect.html'
    context_object_name = 'prospects'

    def get_queryset(self):
        # Filter the queryset to only include prospects with 'Failed' status
        return Prospect.objects.filter(status='Review', company=self.request.user.active_company.name).order_by('created_at')

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
    if request.user.active_company:
        # Retrieve the prospect and API URL
        api_url = f'{request.user.active_company.api}/prospects/{slug}/'
        prospect = get_object_or_404(Prospect, slug=slug)

        if request.method == 'POST':
            # Get the decline reason from the request
            decline_reason = request.POST.get('declinereason', '')

            if not decline_reason:
                messages.error(request, 'Decline reason is required.')
                return redirect(reverse('valuation_prospect_detail', kwargs={'slug': prospect.slug}))

            try:
                # Update the prospect status in the upstream system
                prospect_response = requests.patch(
                    api_url,
                    data={
                        "status": "Declined",
                        "decline_reason": decline_reason,
                        "proof_of_payment_id": "",
                    },
                )

                # Update the local prospect status if upstream update was successful
                if 200 <= prospect_response.status_code <= 399:
                    prospect.status = "Declined"
                    prospect.decline_reason = f"Valuation-{decline_reason}"
                    prospect.save()
                    messages.success(request, 'Prospect declined successfully.')
                    return redirect('prospect_pending')

            except requests.RequestException as e:
                # Handle exceptions from the API call
                messages.error(request, f"An error occurred while updating the prospect: {str(e)}")

        # Render the decline form
        context = {
            "page_name": "valuation",
            'prospect': prospect,
            "sub_page_name": "declined_valuation_prospects"
        }
        return render(request, 'prospects/decline_form.html', context)
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')


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
    if request.user.active_company:
        if request.method == "POST":
            data = json.loads(request.body)
            payment_id = data.get('payment_id', None)
            # print('payment_id',payment_id)
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

            if prospect:
                # confirm trans_id is matching
                if payment_id == prospect['proof_of_payment_id']:
                    # print('I reach there.')
                    # Update prospect's status to "Payment Verified"
                    api_url = f'{request.user.active_company.api}/prospects/{slug}/'
                    # assign valuer
                    users_with_permission = User.objects.filter(
                        # role__permissions__code='can_view_valuation_requests',
                        role__permissions__code='can_be_valuers',
                        company=request.user.company
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
                        if valuer.name not in valuer_assignment_dict:
                            least_assigned_valuer = valuer
                            break
                        # If valuer has the least assignments, choose them
                        if least_assigned_valuer is None or valuer_assignment_dict[valuer.name] < valuer_assignment_dict[least_assigned_valuer.name]:
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


            # Retrieve all users with 'can_be_valuers' permission in the user's active company

        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')


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
    if request.user.active_company:
        api_url = f'{request.user.active_company.api}/prospects/{slug}/'

        response = requests.patch(api_url, data={
            "submitted_for_valuation_by" : request.user.username,
            "submitted_for_valuation_on" : datetime.now(),
            "status" : 'Valuation'
        })
        if response.status_code >= 200 and response.status_code <= 399:
            # was successful
            #set prospect status on local
            prospect = Prospect.objects.filter(slug=slug).first()
            prospect.status = 'Valuation'
            prospect.save()

            vehicle = VehicleAsset.objects.filter(prospect=prospect).first()
            valuer_assigned = prospect.valuer_assigned

            if valuer_assigned:
                # Split the valuer_assigned into first_name and last_name if it contains a space
                name_parts = valuer_assigned.split(" ")

                # Use Q objects to filter by username or full name
                if len(name_parts) == 2:  # If it's "FirstName LastName"
                    user = User.objects.filter(
                        Q(username=valuer_assigned) |
                        Q(first_name=name_parts[0], last_name=name_parts[1])
                    ).first()
                else:  # If it's just the username
                    user = User.objects.filter(username=valuer_assigned).first()

                if user:
                    # Send the email if a user is found

                    subject =  "Received Prospect {} for Valuation.".format(prospect).upper()
                    email = user.email
                    message = f"You have been assigned a prospect for valuation. Please log in to continue.\n\nProspect: {str(prospect).upper()} - {prospect.phone_number}\nVehicle: {str(vehicle).upper()}\nValuer: {str(valuer_assigned).upper()}\n"

                    send_email_task(subject, email, message)
                    messages.success(request, "Prospect: {} assigned to valuer: {} successfully and email sent for notification.".format(prospect, valuer_assigned).upper())
                else:
                    # Handle the case where no matching user is found
                    messages.error(request, "No matching user found for the assigned valuer.")
                return redirect(reverse_lazy("prospect_valuation"))
            return redirect('prospect_valuation')
        else:
            return redirect(reverse_lazy("prospect_detail", args=[slug]))
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')

# View for adding evaluation report details for a particular prospect
@login_required
def add_valuation_report_details(request, slug):
    if request.user.active_company:

        api_url = f'{request.user.active_company.api}/prospects/{slug}/'
        if Prospect.objects.filter(slug=slug):
            prospect = Prospect.objects.filter(slug=slug).first()
        else:
            # fetch and save prospect
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()

            for prospect in data:
                    prospect['prospect'] = prospect.id

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
            messages.error("Prospect not found")
            return redirect("prospect_valuation")

        context = {
            "page_name": "valuation",
            'prospect': prospect,
            "sub_page_name" : "valuation_requests",
        }

        if request.method == 'POST':
            prospect = Prospect.objects.filter(slug=slug).first()
            # Vehicles
            v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect).order_by('-created_at')
            if not v_reports:
                form = VehicleEvaluationReportForm(request.POST, request.FILES, prospect=prospect)
                if form.is_valid():

                    # check if the tax_identification_number is numeric
                    if not str(form.cleaned_data['tax_identification_number']).isdigit() or len(str(form.cleaned_data['tax_identification_number'])) != 10:
                        messages.error(request, "Tax Identification Number should only contain 10 numeric values.")
                        return redirect('valuation_prospect_detail', slug=slug)

                    if VehicleEvaluationReport.objects.filter(tax_identification_number=form.cleaned_data['tax_identification_number']).exists():
                        messages.error(request, "Tax Identification Number already exists in our database, Please provide a unique Tax Identification Number.")
                        return redirect('valuation_prospect_detail', slug=slug)

                    # check if the length of power exeeds 5 characters
                    if len(str(form.cleaned_data['power'])) >= 5:
                        messages.error(request, "Power value supplied can not exceed 5 digits in length. Please try again.")
                        return redirect('valuation_prospect_detail', slug=slug)

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

                        # supervisor = User.objects.filter(Q(role__permission__code=('can_be_supervisor')) | Q(role__permission__code=('can_perform_admin_functions'))).first()
                        supervisor = User.objects.filter(role__permissions__code=('can_be_supervisor' and 'can_verify_payment')).first()
                        if supervisor:
                            subject = 'New Prospect Valuation Supervision Request for prospect {}.'.format(prospect.name)
                            email = supervisor.email
                            message =  f'Hi {supervisor},\n\nYou have a new Prospect Valuation Supervision Request. Below are the details.\n\nProspect: {prospect.name}\nPhone: {prospect.phone_number}\n'

                            send_email_task(subject, email, message)


                    # Redirect to the 'valuation_prospect_detail' page
                    messages.add_message(request, messages.SUCCESS, "Asset Valuation submitted successfully")
                    return redirect('valuation_prospect_detail', slug=slug)
                else:
                    messages.add_message(request, messages.ERROR, "ERROR MODIFYING RECORDS. TRY AGAIN!!")
                    return redirect('valuation_prospect_detail', slug=slug)
            else:
                # save edited data
                submitted_report_id = request.GET.get("form_id")
                if submitted_report_id:
                    report = VehicleEvaluationReport.objects.filter(pk=submitted_report_id)
                    # save updated data
                    if not report:
                        messages.add_message(request, messages.ERROR, "REPORT NOT FOUND. TRY AGAIN!")
                    else:
                        form = VehicleEvaluationReportForm(request.POST, request.FILES, instance=report.first(), prospect=prospect,
                            initial={
                        "date_of_registration": report.first().date_of_registration,
                        "date_of_valuation": report.first().date_of_valuation,
                        "valuation_report_date": report.first().valuation_report_date,
                    })
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
            if v_reports.exists():
                # prospect.status = 'Valuation Supervisor' --> don't put prospect status here.

                context["v_reports"] = [
                    {"form": VehicleEvaluationReportForm(
                        instance=report,
                        prospect=prospect,
                    initial={
                        "date_of_registration": report.date_of_registration,
                        "date_of_valuation": report.date_of_valuation,
                        "valuation_report_date": report.valuation_report_date,
                    }
                    ),
                    "report": report,
                    }
                    for report in v_reports
                    ]
            else:
                context["create_vehicle_report_form"] = VehicleEvaluationReportForm(
                    prospect=prospect,
                    )
        return render(request, 'valuations/evaluation_report_form.html', context=context)
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')


@login_required
def add_another_valuation_report_details(request, slug):
    if request.user.active_company:

        api_url = f'{request.user.active_company.api}/prospects/{slug}/'
        prospect = Prospect.objects.filter(slug=slug).first()
        context = {
            "page_name": "valuation",
            'prospect': prospect,
            "sub_page_name" : "valuation_requests",
        }

        if request.method == 'POST':
            prospect = Prospect.objects.filter(slug=slug).first()
            # Vehicles
            v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
            # if not v_reports:
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
                return redirect('valuation_prospect_detail', slug=slug)
            else:
                messages.add_message(request, messages.ERROR, "ERROR MODIFYING RECORDS. TRY AGAIN!!")
        # else:
        #     # save edited data
        #     submitted_report_id = request.GET.get("form_id")
        #     if submitted_report_id:
        #         report = VehicleEvaluationReport.objects.filter(pk=submitted_report_id)
        #         # save updated data
        #         if not report:
        #             messages.add_message(request, messages.ERROR, "REPORT NOT FOUND. TRY AGAIN!")
        #         else:
        #             form = VehicleEvaluationReportForm(request.POST, request.FILES, instance=report.first(), prospect=prospect,
        #                 initial={
        #             "date_of_registration": report.first().date_of_registration,
        #             "date_of_valuation": report.first().date_of_valuation,
        #             "valuation_report_date": report.first().valuation_report_date,
        #         })
        #             if form.is_valid():
        #                 form = form.save(commit=False)
        #                 form.prospect = prospect
        #                 # form.prospect.status = 'Valuation Supervisor'
        #                 form.save()
        #                 # prospect.status = 'Review'

        #                 # update upstream prospect status
        #                 response = requests.patch(api_url, data={
        #                     "status" : prospect.status,
        #                     "valuation_submitted_on" : datetime.now(),
        #                     "valuation_submitted_by" : request.user.username,
        #                 })
        #                 if response.status_code >= 200 and response.status_code <= 399:
        #                     prospect.status = prospect.status
        #                     prospect.valuation_submitted_on = datetime.now()
        #                     prospect.valuation_submitted_by = request.user

        #                 messages.add_message(request, messages.SUCCESS, "RECORDS MODIFIED SUCCESSFULLY")

        #     # redirect to details page if form id is found or not
        #     return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

        else:
            prospect = Prospect.objects.filter(slug=slug).first()

            # v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
            # if v_reports.exists():
            #     # prospect.status = 'Valuation Supervisor' --> don't put prospect status here.

            #     context["v_reports"] = [
            #         {"form": VehicleEvaluationReportForm(
            #             instance=report,
            #             prospect=prospect,
            #         initial={
            #             "date_of_registration": report.date_of_registration,
            #             "date_of_valuation": report.date_of_valuation,
            #             "valuation_report_date": report.valuation_report_date,
            #         }
            #         ),
            #         "report": report,
            #         }
            #         for report in v_reports
            #         ]
            # else:
            context["create_vehicle_report_form"] = VehicleEvaluationReportForm(
                prospect=prospect,
                    # initial={
                    #     "date_of_registration": v_reports.date_of_registration,
                    #     "date_of_valuation": v_reports.date_of_valuation,
                    #     "valuation_report_date": v_reports.valuation_report_date,
                    # }
                )


        return render(request, 'valuations/another_evaluation_report_form.html', context=context)
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')

@login_required
def add_inspection_report_details(request, slug):
    if request.user.active_company:
        # print('\n\n\n add inspection repot detiaks caleld')
        api_url = f'{request.user.active_company.api}/prospects/{slug}/'

        print('this si it', Prospect.objects.filter(slug=slug).first())
        prospect = Prospect.objects.filter(slug=slug).first()

        print('\n\n\n found prospect to be', prospect)
        if not prospect:
            # fetch and save prospect
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if Prospect.objects.filter(slug=slug):
                prospect = Prospect.objects.filter(slug=slug).first() if Prospect.objects.filter(slug=slug).first() else Prospect.objects.filter(slug=slug).first().pk
                serializer = ApiSerializers.ProspectSerializer(prospect, data=data, partial=True)
            else:
                serializer = ApiSerializers.ProspectSerializer(data=data)

            if serializer.is_valid():
                prospect = serializer.save()

        if not prospect:
            messages.error(request, "Prospect not found")
            return redirect("prospect_valuation")

        context = {
            "page_name": "valuation",
            "prospect": prospect,
            "sub_page_name": "valuation_requests",
        }

        if request.method == 'POST':
            print('at point od posting report')
            i_reports = VehicleInspectionReport.objects.filter(vehicle__prospect=prospect)
            print('\n\n', i_reports)
            print('got i reports')
            if not i_reports:
                print('no i reports')
                form = VehicleInspectionReportForm(request.POST, prospect=prospect)
                print('n\n\n form', form)
                if form.is_valid():
                    form = form.save(commit=False)
                    form.prospect = prospect
                    form.save()
                    print('successufl')

                    messages.add_message(request, messages.SUCCESS, "Asset Valuation submitted successfully")
                    return redirect('valuation_prospect_detail', slug=slug)
                else:
                    print('\n\n\n form errors', form.errors)
                    messages.add_message(request, messages.ERROR, "ERROR MODIFYING RECORDS. TRY AGAIN!!")
            else:
                print('some i reports')
                submitted_report_id = request.GET.get("form_id")
                print('\n\n\n  repot id', submitted_report_id)
                if submitted_report_id:
                    report = VehicleInspectionReport.objects.filter(pk=submitted_report_id).first()
                    print('report', report)
                    if not report:
                        messages.add_message(request, messages.ERROR, "REPORT NOT FOUND. TRY AGAIN!")
                    else:
                        form = VehicleInspectionReportForm(request.POST, instance=report, prospect=prospect)
                        if form.is_valid():
                            form = form.save(commit=False)
                            form.prospect = prospect
                            form.save()
                            print('sucess')
                            messages.add_message(request, messages.SUCCESS, "RECORDS MODIFIED SUCCESSFULLY")
                    return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))
                else:
                    messages.add_message(request, messages.ERROR, 'No form Id found')

        else:
            context["create_inspection_report_form"] = VehicleInspectionReportForm(prospect=prospect)

        return render(request, 'valuations/inspection_report_form.html', context=context)
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')



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
    if request.user.active_company:

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
            context['v_evaluation_reports'] = VehicleEvaluationReport.objects.filter(vehicle__in=vehicle_assets).order_by('-created_at')

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
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')

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
def print_inspection_report(request, slug):
    # Get the prospect and related evaluation report
    prospect = get_object_or_404(Prospect, slug=slug)
    inspection_report = get_object_or_404(VehicleInspectionReport, prospect=prospect)

    # Pass the data to a print-friendly template
    context = {
        "page_name": "valuation_print",
        "prospect": prospect,
        "inspection_report": inspection_report,
        "user": request.user
    }

    return render(request, 'valuations/InspectionReportPrint.html', context=context)


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




# @login_required
# def PipelineView(request, slug):
#     prospect = get_object_or_404(Prospect, slug=slug)
#     api_url_prospect_test = f'{request.user.active_company.api}/vehicles/?prospect={slug}'

#     response = requests.get(api_url_prospect_test)
#     response.raise_for_status()
#     data = response.json()
#     print('\n\n\n\n Data for prospect',data)


#     if request.method == 'POST':
#         v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
#         l_reports = LandEvaluationReport.objects.filter(land__prospect=prospect)
#         # vehicle['prospect'] = data[0]['prospect']
#         # api_url_prospect = f'{request.user.active_company.api}/prospects/{slug}/'

#         # response = requests.get(api_url_prospect)
#         # response.raise_for_status()
#         # data = response.json()

#         if v_reports or l_reports:
#             for v_report in v_reports:
#                 print('\n\n\n V report',v_report)
#                 # prospect.id = data[0]
#                 # print(prospect.id)
#                 serializer = ApiSerializers.VehicleEvaluationReportSerializer(v_report)
#                 api_url = f'{request.user.active_company.api}/vehicle-reports/'

#                 # Prepare files
#                 files = {
#                     "right_hand_side_view": open(f"{settings.BASE_DIR}{serializer.data.get('right_hand_side_view')}", "rb"),
#                     "left_hand_eside_view": open(f"{settings.BASE_DIR}{serializer.data.get('left_hand_eside_view')}", "rb"),
#                     "engine_compartment": open(f"{settings.BASE_DIR}{serializer.data.get('engine_compartment')}", "rb"),
#                     "upholstery": open(f"{settings.BASE_DIR}{serializer.data.get('upholstery')}", "rb"),
#                     "vehicle_id_plate": open(f"{settings.BASE_DIR}{serializer.data.get('vehicle_id_plate')}", "rb"),
#                 }

#                 # Remove file fields from data
#                 file_fields = ['right_hand_side_view', 'left_hand_eside_view', 'engine_compartment', 'upholstery', 'vehicle_id_plate']
#                 for field in file_fields:
#                     serializer.data.pop(field, None)



#                 response = requests.post(api_url, data=serializer.data, files=files)
#                 # print(response.status_code, response.text)
#                 print(f"\n\n\n\n Status Code: {response.status_code}")
#                 print(f"Response Text: {response.text}")  # The server's error message or details
#                 print(f"Response Headers: {response.headers}")  # Headers returned by the server
#                 print(f"Request URL: {response.request.url}")  # URL used for the request
#                 print(f"Request Method: {response.request.method}")  # HTTP method used (GET, POST, etc.)
#                 print(f"Request Headers: {response.request.headers}")  # Headers sent in the request
#                 # print(f"Request Body: {response.request.body}")  # Data sent in the request body


#                 if 200 <= response.status_code <= 399:
#                     api_url = f'{request.user.active_company.api}/prospects/{slug}/'
#                     response = requests.patch(api_url, data={
#                         "status": "Pipeline",
#                         "valuation_reviewd_on": datetime.now(),
#                         "valuation_reviewd_by": request.user.username,
#                     })

#                     if 200 <= response.status_code <= 399:
#                         prospect.status = 'Pipeline'
#                         prospect.valuation_reviewd_on = datetime.now()
#                         prospect.valuation_reviewd_by = request.user
#                         prospect.save()

#             return redirect(reverse_lazy("prospect_review"))

#         messages.error(request, "NO VALUATION REPORT FOUND FOR THIS PROSPECT!")
#     return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))


# END OF VIEWS FOR HANDLING THE LOAN APPLICATION FROM THE BASE.HTML

# login_view
# def PipelineView(request, slug):
#     # Get the prospect object
#     prospect = get_object_or_404(Prospect, slug=slug)

#     # Check if the request is a POST request to handle the form submission
#     if request.method == 'POST':

#         # check for vehicle or land valuation report
#         v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
#         l_reports = LandEvaluationReport.objects.filter(land__prospect=prospect)


#         # if this prospect has a valuation report proceed
#         if v_reports or l_reports:
#             # submit reports to upstream
#             for v_report in v_reports:
#                 serializer = ApiSerializers.VehicleEvaluationReportSerializer(v_report)

#                 api_url = f'{request.user.active_company.api}/vehicle-reports/'
#                 # handle images

#                 files = {
#                     "right_hand_side_view": open(f"{settings.BASE_DIR}{serializer.data.get("right_hand_side_view")}", "rb"),
#                     "left_hand_eside_view": open(f"{settings.BASE_DIR}{serializer.data.get("left_hand_eside_view")}", "rb"),
#                     "engine_compartment": open(f"{settings.BASE_DIR}{serializer.data.get("engine_compartment")}", "rb"),
#                     "upholstery": open(f"{settings.BASE_DIR}{serializer.data.get("upholstery")}", "rb"),
#                     "vehicle_id_plate": open(f"{settings.BASE_DIR}{serializer.data.get("vehicle_id_plate")}", "rb"),
#                 }
#                 serializer.data.pop('right_hand_side_view', None)
#                 serializer.data.pop('left_hand_eside_view', None)
#                 serializer.data.pop('engine_compartment', None)
#                 serializer.data.pop('upholstery', None)
#                 serializer.data.pop('vehicle_id_plate', None)
#                 # serializer.data['pk'] = v_report.prospect.pk

#                 response = requests.post(api_url, data=serializer.data, files=files)

#                 if response.status_code >= 200 and response.status_code <= 399:

#                     api_url = f'{request.user.active_company.api}/prospects/{slug}/'
#                     response = requests.patch(api_url, data={
#                         "status" : 'Pipeline',
#                         "valuation_reviewd_on" : datetime.now(),
#                         "valuation_reviewd_by" : request.user.username,
#                     })


#                     if response.status_code >= 200 and response.status_code <= 399:
#                         prospect.status = 'Pipeline'
#                         prospect.valuation_reviewd_on = datetime.now()
#                         prospect.valuation_reviewd_by = request.user
#                         prospect.save()

#             return redirect(reverse_lazy("prospect_review"))


#         messages.add_message(request, messages.ERROR, "NO VALUATION REPORT FOUND FOR THIS PROSPECT!")
#     return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))


from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf import settings
# from myapp.api.serializers import ApiSerializers

def retry_post(url, payload, files=None, headers=None, retries=3, delay=5):
    """Helper function to retry POST requests."""
    for attempt in range(retries):
        response = requests.post(url, data=payload, files=files, headers=headers)
        if 200 <= response.status_code <= 399:
            return response
        sleep(delay)
    response.raise_for_status()

# def PipelineView(request, slug):
#     # Get the prospect object
#     prospect = get_object_or_404(Prospect, slug=slug)

#     # Check if the request is a POST request to handle the form submission
#     if request.method == 'POST':
#         # Check for vehicle or land valuation reports
#         v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect)
#         l_reports = LandEvaluationReport.objects.filter(land__prospect=prospect)

#         # If this prospect has a valuation report, proceed
#         if v_reports or l_reports:
#             # Submit reports to upstream
#             try:
#                 for v_report in v_reports:
#                     # Serialize the vehicle report
#                     serializer = ApiSerializers.VehicleEvaluationReportSerializer(v_report)
#                     api_url = f'{request.user.active_company.api}/vehicle-reports/'

#                     # Handle images
#                     files = {}
#                     try:
#                         file_fields = [
#                             "right_hand_side_view",
#                             "left_hand_eside_view",
#                             "engine_compartment",
#                             "upholstery",
#                             "vehicle_id_plate",
#                         ]

#                         for field in file_fields:
#                             file_path = serializer.data.get(field)
#                             if file_path:
#                                 files[field] = open(f"{settings.BASE_DIR}{file_path}", "rb")
#                                 serializer.data.pop(field, None)

#                         # Post data to the external API
#                         response = requests.post(api_url, data=serializer.data, files=files)

#                         print(response.status_code, response.text)

#                         # Update prospect status upstream if successful
#                         prospect_api_url = f'{request.user.active_company.api}/prospects/{slug}/'
#                         prospect_response = requests.patch(
#                             prospect_api_url,
#                             data={
#                                 "status": "Pipeline",
#                                 "valuation_reviewd_on": datetime.now().isoformat(),
#                                 "valuation_reviewd_by": request.user.username,
#                             },
#                         )

#                         # Update local prospect status
#                         if 200 <= prospect_response.status_code <= 399:
#                             prospect.status = "Pipeline"
#                             prospect.valuation_reviewd_on = datetime.now()
#                             prospect.valuation_reviewd_by = request.user
#                             prospect.save()

#                     finally:
#                         # Close all file handles
#                         for file in files.values():
#                             file.close()

#                 return redirect(reverse_lazy("prospect_review"))

#             except Exception as e:
#                 # Log the error and show a message to the user
#                 messages.add_message(request, messages.ERROR, f"Error submitting report: {str(e)}")
#                 return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

#         # No valuation report found
#         messages.add_message(request, messages.ERROR, "NO VALUATION REPORT FOUND FOR THIS PROSPECT!")
#         return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

#     # For non-POST requests, redirect to valuation detail page
#     return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))


def PipelineView(request, slug):
    if request.user.active_company:
        # Get the prospect object
        prospect = get_object_or_404(Prospect, slug=slug)

        # Check if the request is a POST request to handle the form submission
        if request.method == 'POST':
            # Check for vehicle or land valuation reports
            v_reports = VehicleEvaluationReport.objects.filter(vehicle__prospect=prospect).order_by('-created_at')
            l_reports = LandEvaluationReport.objects.filter(land__prospect=prospect)

            # If this prospect has a valuation report, proceed
            if v_reports or l_reports:
                try:
                    for v_report in v_reports:
                        # Fetch the associated vehicle data
                        vehicle = v_report.vehicle
                        if not vehicle:
                            continue  # Skip if no vehicle associated


                        # Use external API to fetch the vehicle details
                        # vehicle_api_url = f"{request.user.active_company.api}/vehicles/"
                        vehicle_api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
                        # params = {"chassis_number": vehicle.chassis_number}
                        response = requests.get(vehicle_api_url)
                        response.raise_for_status()
                        # resp_veh = response.json()



                        if response.status_code != 200:
                            messages.error(request, "Failed to fetch vehicle data from the external system.")
                            return redirect(reverse_lazy("valuation_prospect_detail", slug=slug))

                        vehicle_data = response.json()
                        external_vehicle_id = vehicle_data[0]['id']
                        external_prospect_id = vehicle_data[0]['prospect']

                        if not external_vehicle_id or not external_prospect_id:
                            messages.error(request, "Incomplete vehicle data fetched from the external system.")
                            return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

                        # Serialize the vehicle report
                        serializer = ApiSerializers.VehicleEvaluationReportSerializer(v_report)

                        # Modify the data to include the correct vehicle and prospect IDs
                        modified_data = serializer.data.copy()
                        modified_data['vehicle'] = external_vehicle_id
                        modified_data['prospect'] = external_prospect_id

                        # Prepare the API URL
                        api_url = f'{request.user.active_company.api}/vehicle-reports/'

                        # Handle images
                        files = {}
                        try:
                            file_fields = [
                                "front_right_hand_side_view",
                                "front_left_hand_eside_view",
                                "back_right_hand_side_view",
                                "back_left_hand_side_view",
                                "engine_compartment",
                                "upholstery",
                                "vehicle_id_plate",
                            ]

                            for field in file_fields:
                                file_path = modified_data.get(field)
                                if file_path:
                                    files[field] = open(f"{settings.BASE_DIR}{file_path}", "rb")
                                    modified_data.pop(field, None)

                            # checck if report exists,
                            response = requests.get(f"{api_url}{v_report.slug}/")
                            if response.status_code >= 200 and response.status_code <= 299:
                                # successful
                                response = requests.patch(f"{api_url}{v_report.slug}/", data=modified_data, files=files)
                                if not (response.status_code >= 200 and response.status_code <= 299):
                                    messages.add_message(request, messages.ERROR, f"Error submitting report")
                                    return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))
                            else:
                                # Post modified data to the external API
                                response = requests.post(api_url, data=modified_data, files=files)
                                if not (response.status_code >= 200 and response.status_code <= 299):
                                    messages.add_message(request, messages.ERROR, "Error submitting report")
                                    return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

                            # print(response.status_code, response.text)

                            # Update prospect status upstream if successful
                            prospect_api_url = f'{request.user.active_company.api}/prospects/{slug}/'
                            prospect_response = requests.patch(
                                prospect_api_url,
                                data={
                                    "status": "Pipeline",
                                    "valuation_reviewd_on": datetime.now().isoformat(),
                                    "valuation_reviewd_by": request.user
                                },
                            )

                            # Update local prospect status
                            if 200 <= prospect_response.status_code <= 399:
                                prospect.status = "Pipeline"
                                prospect.valuation_reviewd_on = datetime.now()
                                prospect.valuation_reviewd_by = request.user
                                prospect.save()
                                vehicle.status = "VALUED"
                                vehicle.save()

                        finally:
                            # Close all file handles
                            for file in files.values():
                                file.close()

                    return redirect(reverse_lazy("prospect_review"))

                except Exception as e:
                    # Log the error and show a message to the user
                    messages.add_message(request, messages.ERROR, f"Error submitting report: {str(e)}")
                    return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

            # No valuation report found
            messages.add_message(request, messages.ERROR, "NO VALUATION REPORT FOUND FOR THIS PROSPECT!")
            return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

        # For non-POST requests, redirect to valuation detail page
        return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')

def InspectionPipeline(request, slug):
    if request.user.active_company:
        # Get the prospect object
        prospect = get_object_or_404(Prospect, slug=slug)

        # Check if the request is a POST request to handle the form submission
        if request.method == 'POST':
            # Check for inspection reports
            i_reports = VehicleInspectionReport.objects.filter(vehicle__prospect=prospect)

            # If this prospect has a inspection report, proceed
            if i_reports:
                try:
                    for i_report in i_reports:
                        print(i_report)
                        # Fetch the associated vehicle data
                        vehicle = i_report.vehicle
                        if not vehicle:
                            continue  # Skip if no vehicle associated


                        # Use external API to fetch the vehicle details
                        # vehicle_api_url = f"{request.user.active_company.api}/vehicles/"
                        vehicle_api_url = f'{request.user.active_company.api}/vehicles/?prospect={slug}'
                        # params = {"chassis_number": vehicle.chassis_number}
                        response = requests.get(vehicle_api_url)
                        response.raise_for_status()
                        # resp_veh = response.json()



                        if response.status_code != 200:
                            messages.error(request, "Failed to fetch vehicle data from the external system.")
                            return redirect(reverse_lazy("valuation_prospect_detail", slug=slug))

                        vehicle_data = response.json()
                        external_vehicle_id = vehicle_data[0]['id']
                        external_prospect_id = vehicle_data[0]['prospect']
                        print('\n\n\n external_vehicle_id, external_prospect_id', external_vehicle_id, external_prospect_id)

                        if not external_vehicle_id or not external_prospect_id:
                            messages.error(request, "Incomplete vehicle data fetched from the external system.")
                            return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

                        # Serialize the vehicle report
                        serializer = ApiSerializers.VehicleInspectionReportSerializer(i_report)

                        # Modify the data to include the correct vehicle and prospect IDs
                        modified_data = serializer.data.copy()
                        modified_data['vehicle'] = external_vehicle_id
                        modified_data['prospect'] = external_prospect_id


                        # Prepare the API URL
                        api_url = f'{request.user.active_company.api}/inspection-reports/'

                        # Post modified data to the external API
                        response = requests.post(api_url, data=modified_data)

                        # print(response.status_code, response.text)

                        # Update prospect status upstream if successful
                        prospect_api_url = f'{request.user.active_company.api}/prospects/{slug}/'
                        prospect_response = requests.patch(
                            prospect_api_url,
                            data={
                                "status": "Pipeline",
                            },
                        )

                        # Update local prospect status
                        if 200 <= prospect_response.status_code <= 399:
                            prospect.status = "Pipeline"
                            prospect.save()
                            vehicle.status = "INSPECTED"
                            vehicle.save()



                    return redirect(reverse_lazy("prospect_review"))

                except Exception as e:
                    # Log the error and show a message to the user
                    messages.add_message(request, messages.ERROR, f"Error submitting report: {str(e)}")
                    return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

            # No valuation report found
            messages.add_message(request, messages.ERROR, "NO INSPECTION REPORT FOUND FOR THIS PROSPECT!")
            return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))

        # For non-POST requests, redirect to valuation detail page
        return redirect(reverse_lazy("valuation_prospect_detail", args=[prospect.slug]))
    else:
        messages.error(request, "Please select a loan company to work with before you proceed.")
        return redirect('dashboard')
