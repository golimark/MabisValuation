# from django.contrib.auth.models import User
# from api import serializers
# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework import pagination
# from rest_framework import viewsets, status
# from Valuation import models

# class CustomPagination(pagination.PageNumberPagination):
#     def get_paginated_response(self, data):
#         response = super().get_paginated_response(data).data
#         response['pages_count'] = self.page.paginator.num_pages
#         return Response(response)

# class ProspectViews(viewsets.ModelViewSet):
#     serializer_class = serializers.ProspectSerializer
#     lookup_field = 'slug'
#     pagination_class = CustomPagination
#     queryset = models.Prospect.objects.all()


# class VehicleAssetViews(viewsets.ModelViewSet):
#     serializer_class = serializers.VehicleAssetSerializer
#     lookup_field = 'slug'
#     pagination_class = CustomPagination
#     queryset = models.VehicleAsset.objects.all()

# class LandAssetViews(viewsets.ModelViewSet):
#     serializer_class = serializers.LandAssetSerializer
#     lookup_field = 'slug'
#     pagination_class = CustomPagination
#     queryset = models.LandEvaluationReport.objects.all()

# class VechicleReportsViews(viewsets.ModelViewSet):
#     serializer_class = serializers.VehicleEvaluationReportSerializer
#     lookup_field = 'slug'
#     pagination_class = CustomPagination
#     queryset = models.VehicleEvaluationReport.objects.all()

# class LandReportsViews(viewsets.ModelViewSet):
#     serializer_class = serializers.LandEvaluationReportSerializer
#     lookup_field = 'slug'
#     pagination_class = CustomPagination
#     queryset = models.LandEvaluationReport.objects.all()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import User, Company
from .serializers import UserSerializer, CompanySerializer
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet

class UserViewSet(ReadOnlyModelViewSet):  # Use ReadOnlyModelViewSet for GET-only views
    queryset = User.objects.all()
    serializer_class = UserSerializer
    


class CompanyViewSet(ReadOnlyModelViewSet):  # Use ReadOnlyModelViewSet for GET-only views
    queryset = Company.objects.all()
    serializer_class = CompanySerializer



# class ProspectViews(viewsets.ModelViewSet):
#     serializer_class = serializers.ProspectSerializer
#     lookup_field = 'slug'
#     pagination_class = CustomPagination
#     filter_backends = [CustomStatusFilter]
#     queryset = Prospect.objects.filter(Q(status='Pending') | Q(status='Valuation') | Q(status='Valuation Supervisor') | Q(status='Inspection') | Q(status='Payment Verified') | Q(status='Review'))
