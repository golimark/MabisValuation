from rest_framework import serializers
from prospects.models import *
from Valuation.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'status', 'image', 'slug', 'created_at', 'updated_at',
            'company', 'active_company', 'role', 'permissions', 'name'
        ]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        # fields = "__all__"
        exclude = ("agent", "created_by")

class VehicleAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAsset
        fields = "__all__"

class VehicleEvaluationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleEvaluationReport
        exclude = ["fields"]

class VehicleInspectionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInspectionReport
        fields = "__all__"


class LandAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandAsset
        fields = "__all__"

class LandEvaluationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandEvaluationReport
        exclude = ["fields"]

class ProofofPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofofPayment
        fields = "__all__"
