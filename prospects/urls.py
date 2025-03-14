from django.urls import path
from . import views
from .views import *

urlpatterns = [


    #REMARKS
    # path('remarks/', remarks_view, name='remarks_view'),
    # path('valuer-remarks/', ValuerRemarksView.as_view(), name='valuer_remarks'),
    # path('supervisor-remarks/', SupervisorRemarksView.as_view(), name='supervisor_remarks'),
    # path('approver-remarks/', ApproverRemarksView.as_view(), name='approver_remarks'),

    # prospects menu
    path('', ProspectListView.as_view(), name='prospect_list'),
    path('create/', ProspectCreateView.as_view(), name='prospect_create'),
    path('details/<str:slug>', ProspectDetailView.as_view(), name='prospect_detail'),
    path('prospect-details/<str:slug>', ProspectDetailViewforNewProspects.as_view(), name='prospect_detail_new_prospects'),
    path('pending/', ProspectPendingView.as_view(), name='prospect_pending'),
    path('declined/', ProspectDeclinedView.as_view(), name='prospect_declined'),
    path('failed/', ProspectFailedView.as_view(), name='prospect_failed'),
    path('restore_from_decline/<str:slug>', ProspectRestoreFromDecline.as_view(), name='restore_prospect_fr_decline'),
    path('restore_from_failed/<str:slug>', ProspectRestoreFromFailed.as_view(), name='restore_prospect_fr_failed'),
    path('valuation/print/<slug:slug>/', views.print_valuation_report, name='print_valuation_report'),
    path('inspection/print/<slug:slug>/', views.print_inspection_report, name='print_inspection_report'),
    path('print/<slug:slug>', views.printout_report, name='print_report'),
    path('drafts-reports/', views.drafts_list, name='draft_list'), 
    path('drafts-report/<str:slug>/editing/', views.edit_draft, name='draft_editing'), 
    path('drafts-report/<str:slug>/delete/', views.delete_draft, name='delete_draft'), 


    # valuation menu
    path('valuations/', ValuationProspectListView.as_view(), name='valuations_prospect_list'),
    path('pending-valuation/', ValuationProspectPendingView.as_view(), name='valuation_prospect_pending'),
    path('valuation-details/<str:slug>/', ValuationProspectDetailView.as_view(), name='valuation_prospect_detail'), 
    path('valuation-prospect-details/<str:slug>/', ValuationProspectDetailViewforNewProspects.as_view(), name='valuation_prospect_detail_new_prospect'), 
    path('valuation/', ProspectValuationView.as_view(), name='prospect_valuation'),
    path('manualy-assign-valuer/<str:slug>/', ManuallyAssignNewValuer.as_view(), name='manually_assign_valuer'),
    path('auto_assign-valuer/<str:slug>/', AutoAssignNewValuer.as_view(), name='auto_assign_valuer'),
    path('inspection-requests/', InspectionView.as_view(), name='prospect_inspection'),
    path('review/', ProspectReviewView.as_view(), name='prospect_review'),
    path('supervisor-review/', ProspectSupervisorReviewView.as_view(), name='prospect_supervisor_review'),
    path('decline/<str:slug>/', views.DeclineView, name='decline'),

    # valuation subprocesses
    path('valuate/<str:slug>/', views.prospect_in_valuation, name='valuate_prospect'),
    path('valuation-set/<str:slug>/', views.set_valuation, name='set_valuation'),
    path('add-valuation/<str:slug>/', views.add_valuation_report_details, name='create_valuation_report'),
    path('add-inspection/<str:slug>/', views.add_inspection_report_details, name='create_inspection_report'),
    path('add-another-valuation/<str:slug>/', views.add_another_valuation_report_details, name='create_another_valuation_report'),
    path('view-valuation/<str:slug>/', views.view_valuation_report, name='valuation_report'),
    path('submit-report/<str:slug>/', views.submit_report, name='submit_report'),

    path('pipeline/<str:slug>/', views.PipelineView, name='pipeline'),

    path('inspection/<str:slug>/', views.InspectionPipeline, name='inspection-pipeline'),

]
