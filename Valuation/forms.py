
from django import forms
from .models import *
from accounts.models import *
from django.db.models import Q


    
    
class VehicleEvaluationReportForm(forms.ModelForm):
    class Meta:
        model = VehicleEvaluationReport
        exclude = ["prospect", "slug", "created_at", "updated_at"]
        fields = [
            'vehicle', 'name_in_logbook', 'tax_identification_number', 'date_of_registration', 'maketypes','make', 'model', 'body_description','engine_number', 'chassis_number','mileage', 'power', 'fuel_type', 'gearbox_transmission', 'country_of_origin','year_of_manufacture',
            'years_since_on_uganda_roads','color_by_logbook', 'color_by_inspection' ,'seating_capacity','place_of_inspection',
            'date_of_valuation', 'valuation_report_date',
            'chassis_frame', 'body_shell_paint', 'condition_of_seats', 'engine_assembly',
            'accessories', 'cooling_system', 'gearbox_assembly', 'transmission_system',
            'steering_system', 'suspension', 'braking_system', 'electrical_system',
            'windshield', 'air_conditioning_system', 'wheels', 'tyre_condition', 'road_test',
            'insurance_valuation', 'forced_sale', 'market_value', 'limiting_conditions',
            'effective_report_summary', 'valuation', 'market_value_description',
            'current_value_description', 'recommendation', 'front_right_hand_side_view',
            'front_left_hand_eside_view','back_right_hand_side_view','back_left_hand_side_view', 'engine_compartment', 'upholstery', 'vehicle_id_plate', 
            'company_supervisor_remarks', 'company_approver_remarks'
            # 'company_valuer', 'company_valuer_remarks','company_supervisor', 'company_supervisor_remarks','company_approver', 'company_approver_remarks'
        ]

        widgets = {
            'date_of_valuation': forms.DateTimeInput(attrs={
                'class': 'form-control',
            }),
        }

    # def clean_date_field(self):
    #     date_of_registration = self.cleaned_data['date_of_registration']
    #     # Convert date format if needed
    #     if date_of_registration:
    #         return date_of_registration.strftime('%d/%m/%Y')
    #     return date_of_registration
    def __init__(self, *args, **kwargs):
        prospect = kwargs.pop('prospect', None)
        vehicle = kwargs.pop('vehicle', None)
        user = kwargs.pop('user', None)
        super(VehicleEvaluationReportForm, self).__init__(*args, **kwargs)

        
        # Custom labels
        self.fields['tax_identification_number'].label = "Tax ID Number"
        self.fields['market_value'].required = True

        # Make image fields required
        image_fields = [
            'front_right_hand_side_view', 'front_left_hand_eside_view', 'back_right_hand_side_view', 'back_left_hand_side_view', 'engine_compartment',
            'upholstery', 'vehicle_id_plate'
        ]
        for field_name in image_fields:
            self.fields[field_name].required = True

        # Set classes for all fields and customize certain fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name in ['insurance_valuation', 'forced_sale', 'market_value']:
                field.widget.attrs.update({'id': f'id_v_{field_name}', 'data-attribute': field_name})
            
        # Set date fields with dd/mm/yyyy format
        date_fields = ['date_of_registration', 'valuation_report_date']
        for date_field in date_fields:
            self.fields[date_field].widget = forms.DateInput(
                # format='%d/%m/%Y',
                attrs={'type': 'date', 'placeholder': 'dd/mm/yyyy'}
            )
            # self.fields[date_field].input_formats = ['%d/%m/%Y']


        if prospect.status == 'Valuation':
            self.fields['company_supervisor_remarks'].widget = forms.HiddenInput()
            self.fields['company_approver_remarks'].widget = forms.HiddenInput()
            self.fields['company_supervisor_remarks'].disabled = True
            self.fields['company_approver_remarks'].disabled = True

        if prospect.status == 'Valuation Supervisor':
            self.fields['recommendation'].disabled = True
            self.fields['company_approver_remarks'].widget = forms.HiddenInput()
            self.fields['company_approver_remarks'].disabled = True


        if prospect.status == 'Review':
            self.fields['recommendation'].disabled = True
            self.fields['company_supervisor_remarks'].disabled = True
            # self.fields['company_supervisor_remarks'] = forms.TextInput()
        # Custom initialization based on prospec

        # if prospect:
        #     self.fields['vehicle'].queryset = VehicleAsset.objects.filter(prospect=prospect)
        #     self.fields['vehicle'].initial = VehicleAsset.objects.filter(prospect=prospect).first()
        #     self.fields['make'].initial = VehicleAsset.objects.filter(prospect=prospect).first().make
        #     self.fields['model'].initial = VehicleAsset.objects.filter(prospect=prospect).first().model
        #     self.fields['name_in_logbook'].initial = prospect.name
        #     # self.fields['company_valuer'].initial = prospect.valuer_assigned
            # self.fields['company_valuer'].disabled = True



class ValuerRemarksForm(forms.ModelForm):
    class Meta:
        model = VehicleEvaluationReport
        fields = ['company_valuer', 'company_valuer_remarks']




class SupervisorRemarksForm(forms.ModelForm):
    class Meta:
        model = VehicleEvaluationReport
        fields = ['company_supervisor', 'company_supervisor_remarks']



class ApproverRemarksForm(forms.ModelForm):
    class Meta:
        model = VehicleEvaluationReport
        fields = ['company_approver', 'company_approver_remarks']




class LandAssetForm(forms.ModelForm):
    class Meta:
        model = LandAsset
        exclude = ["prospect", "slug", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

            if isinstance(field, (forms.DateField, forms.DateTimeField)):
                field.widget = forms.DateInput(attrs={'type': 'date'})


class LandEvaluationReportForm(forms.ModelForm):

    class Meta:
        model = LandEvaluationReport
        exclude = ["prospect", "slug", "created_at", "updated_at"]

    # Optional: Label customization
    def __init__(self, *args, **kwargs):
        prospect = kwargs.pop('prospect', None)
        super(LandEvaluationReportForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['years_on_road'].initial = self.instance.years_on_road
            # self.fields['years_since_manufacture'].initial = self.instance.years_since_manufacture

        # Label customization (optional)
        self.fields['tax_identification_number'].label = "Tax ID Number"
        self.fields['number_plate'].label = "Number Plate"
        self.fields['make'].label = "Make"

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

            if isinstance(field, (forms.DateField, forms.DateTimeField)):
                field.widget = forms.DateInput(attrs={'type': 'date'})

        if prospect:
            self.fields['vehicle'].queryset = LandAsset.objects.filter(prospect=prospect)

