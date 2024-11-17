from django.urls import path
from . import views
from . views import *

urlpatterns = [
    
    # valuation menu
    # path('valuations/', ValuationProspectListView.as_view(), name='valuations_prospect_list'),
    # path('pending-valuation/', ValuationProspectPendingView.as_view(), name='valuation_prospect_pending'),
    # path('valuation-details/<str:slug>/', ValuationProspectDetailView.as_view(), name='valuation_prospect_detail'),
    # path('valuation/', ProspectValuationView.as_view(), name='prospect_valuation'),
    # path('review/', ProspectReviewView.as_view(), name='prospect_review'),
    # path('decline/<str:slug>/', views.DeclineView, name='decline'),

    # # valuation subprocesses
    # path('valuate/<str:slug>/', views.prospect_in_valuation, name='valuate_prospect'),
    # path('valuation-set/<str:slug>/', views.set_valuation, name='set_valuation'),
    # path('valuation-srpervisor-set/<str:slug>/', views.set_valuation_supervisor, name='set_valuation_supervisor'),
    # path('add-valuation/<str:slug>/', views.add_valuation_report_details, name='create_valuation_report'),
    # path('view-valuation/<str:slug>/', views.view_valuation_report, name='valuation_report'),
    # path('submit-report/<str:slug>/', views.submit_report, name='submit_report'),

    # fetch data 
    path('vehicle-assets', views.fetch_prospects_from_mabis, name='get_data_from_mabis'),
    path('vehicle-asset-data', views.fetch_vehicle_asset_for_prospect, name='get_vehicle_asset_data'),

]
