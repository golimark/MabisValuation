# from django.urls import path
# from rest_framework import routers
# from api import views

# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# # Define the schema view for Swagger
# schema_view = get_schema_view(
#    openapi.Info(
#       title="MABIS API",
#       default_version='v1',
#       description="MABIS API Documentation",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="contact@mabis.local"),
#       license=openapi.License(name="BSD License"),
#    ),
#    public=True,
# )

# api_router = routers.DefaultRouter()
# api_router.register(r'prospects', views.ProspectViews, basename='prospects')
# api_router.register(r'vehicles', views.VehicleAssetViews, basename='vehicle_assets')
# api_router.register(r'land', views.LandAssetViews, basename='land_assets')
# api_router.register(r'vehicle-reports', views.VechicleReportsViews, basename='vehicle_asset_reports')
# api_router.register(r'land-reports', views.LandReportsViews, basename='land_asset_reports')

# urlpatterns = [
#     path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
# ]

# urlpatterns += api_router.urls
