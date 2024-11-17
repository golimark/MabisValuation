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
