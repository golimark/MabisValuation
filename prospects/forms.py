
from django import forms
from .models import *
from accounts.models import *
from Valuation.models import *
from django.db.models import Q





class ProspectCreateForm(forms.ModelForm):
    # agent = forms.ModelChoiceField(queryset=Agent.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Prospect
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
            if field_name == 'gender':
                field.widget.attrs.update({'id': 'gender_id'})
            
            if field_name == 'title':
                field.widget.attrs.update({'id': 'title_id'})

            if field_name == 'phone_number':
                field.widget = forms.NumberInput(attrs={'class': 'form-control'})
            
            if field_name == 'alt_number':
                field.widget = forms.NumberInput(attrs={'class': 'form-control'})
            
            if field_name == 'agent':
                field.widget.attrs.update({'id': 'agent_id', 'style': 'text-transform: uppercase;'})

            if isinstance(field, (forms.DateField, forms.DateTimeField)):
                field.widget = forms.DateInput(attrs={'type': 'date'})

        # if user:
        #     queryset = queryset.filter(company=user.company)

        self.fields['agent'].queryset = Agent.objects.filter(status = "Approved")
        self.fields['company'].widget = forms.HiddenInput()


class ProspectForm(forms.ModelForm):
    # agent = forms.ModelChoiceField(queryset=Agent.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    # car_type = forms.ModelChoiceField(queryset=CarType.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Prospect
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        proof_of_payment_id = cleaned_data.get('proof_of_payment_id')
        if Prospect.objects.filter(proof_of_payment_id=proof_of_payment_id).exists():
            raise forms.ValidationError({"proof_of_payment_id": "This Proof of Payment ID already exists. Please provide a unique ID."})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agent'].disabled = True
        self.fields['agent'].label_from_instance = lambda obj: f"{obj}".upper()

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

            if field_name == 'phone_number':
                field.widget = forms.NumberInput(attrs={'class': 'form-control'})
            
            if field_name == 'alt_number':
                field.widget = forms.NumberInput(attrs={'class': 'form-control'})

            if isinstance(field, (forms.DateField, forms.DateTimeField)):
                field.widget = forms.DateInput(attrs={'type': 'date'})



class VehicleAssetForm(forms.ModelForm):
    class Meta:
        model = VehicleAsset
        exclude = ["prospect", "years_since_manufacture", "slug", "created_at", "updated_at", "status"]
        widgets = {
            'make': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'id_make',
                'style': 'display:none;'  # Hide 'make' field initially
            }),
            'maketypes': forms.Select(attrs={
                'class': 'form-control', 
                'id': 'id_make_types',
                'onchange': 'toggleMakeField()'  # Add JavaScript function to toggle visibility
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Check the initial value of maketypes to determine visibility of make field
        maketype_value = self.initial.get('maketypes', self.data.get('maketypes', None))
       
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'make':  # Ensure the make field has the correct ID
                field.widget.attrs['id'] = 'id_make'

            if field_name == 'maketypes':  # Ensure the make field has the correct ID
                field.widget.attrs['id'] = 'id_make_types'
            

            if isinstance(field, (forms.DateField, forms.DateTimeField)):
                field.widget = forms.DateInput(attrs={'type': 'date'})
                
        self.fields['license_plate'].widget.attrs.update({'style': 'text-transform: uppercase;'})



    
    
class VehicleEvaluationReportForm(forms.ModelForm):
    class Meta:
        model = VehicleEvaluationReport
        exclude = ["prospect", "slug", "created_at", "updated_at"]
        fields = [
            'vehicle', 'name_in_logbook', 'tax_identification_number', 'date_of_registration','make', 'model', 'body_description','engine_number', 'chassis_number','mileage', 'power', 'fuel_type', 'gearbox_transmission', 'country_of_origin','year_of_manufacture',
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
        date_fields = ['date_of_registration', 'date_of_valuation', 'valuation_report_date']
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

        if prospect:
            self.fields['vehicle'].queryset = VehicleAsset.objects.filter(prospect=prospect)
            self.fields['vehicle'].initial = VehicleAsset.objects.filter(prospect=prospect).first()
            self.fields['make'].initial = VehicleAsset.objects.filter(prospect=prospect).first().make
            self.fields['model'].initial = VehicleAsset.objects.filter(prospect=prospect).first().model
            self.fields['name_in_logbook'].initial = prospect.name
            # self.fields['company_valuer'].initial = prospect.valuer_assigned
            # self.fields['company_valuer'].disabled = True


# class VehicleInspectionReportForm(forms.ModelForm):
#     class Meta:
#         model = VehicleInspectionReport
#         exclude = ["client_name", "slug"]

#         def __init__(self, *args, **kwargs):
#             # prospect = kwargs.pop('prospect', None)
#             super(VehicleInspectionReportForm, self).__init__(*args, **kwargs)


#             # Set date fields with dd/mm/yyyy format
#             date_field = ['date']
#             self.fields[date_field].widget = forms.DateInput(
#                 # format='%d/%m/%Y',
#                 attrs={'type': 'date', 'placeholder': 'dd/mm/yyyy'}
#             )
#                 # self.fields[date_field].input_formats = ['%d/%m/%Y']

class VehicleInspectionReportForm(forms.ModelForm):
    class Meta:
        model = VehicleInspectionReport
        exclude = ["prospect", "slug"]
        fields = [
            'vehicle', 'inspector', 'location', 'date', 'reason_for_inspection',
            'ignition_status', 'ignition_comment', 'wind_shield_wipers_status', 'wind_shield_wipers_comment',
            'headlights_status', 'headlights_comment', 'turn_signals_status', 'turn_signals_comment',
            'brake_lights_status', 'brake_lights_comment', 'side_mirrors_status', 'side_mirrors_comment',
            'horn_status', 'horn_comment', 'radio_status', 'radio_comment',
            'body_condition_status', 'body_condition_comment', 'exterior_flashlights_status', 'exterior_flashlights_comment',
            'windows_status', 'windows_comment', 'any_other_abnormalities_status', 'any_other_abnormalities_comment',
            'remarks'
        ]

    def __init__(self, *args, **kwargs):
        prospect = kwargs.pop('prospect', None)
        super(VehicleInspectionReportForm, self).__init__(*args, **kwargs)

        if prospect:
            print('prospect from form is', prospect)
            self.fields['vehicle'].queryset = VehicleAsset.objects.filter(prospect=prospect)
            self.fields['vehicle'].initial = VehicleAsset.objects.filter(prospect=prospect).first()
            self.fields['inspector'].initial = prospect.name

        # Set date fields with 'dd/mm/yyyy' format
        if 'date' in self.fields:
            self.fields['date'].widget = forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/yyyy'}
            )



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

# class CarTypeForm(forms.ModelForm):
#     class Meta:
#         model = CarType
#         fields = ['name']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter car type name'}),
#         }

# class CarModelForm(forms.ModelForm):
#     class Meta:
#         model = CarModel
#         fields = ['name', 'car_type']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter car model name'}),
#             'car_type': forms.Select(attrs={'class': 'form-control'}),
#         }
