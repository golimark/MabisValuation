from rest_framework import serializers
from prospects.models import *
from Valuation.models import *


class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = "__all__"

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
