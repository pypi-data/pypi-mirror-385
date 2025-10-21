from django.urls import path
from .views import admin as vadmin, fc as vfc, review as vrev, user as vuser
app_name = "autosrp"

urlpatterns = [
    path("admin/api/doctrine-hulls/", vadmin.doctrine_hulls, name="api-doctrine-hulls"),
    path("admin/api/doctrine/fits/", vadmin.doctrine_fits, name="api-doctrine-fits"),
    path("admin/api/modules/search/", vadmin.api_search_modules, name="api-mod-search"),

    # Admin GUI
    path("admin/", vadmin.SettingsHome.as_view(), name="admin-home"),
    path("admin/stats/", vadmin.stats, name="admin-stats"),

    path("admin/penalties/", vadmin.PenaltyList.as_view(), name="penalty-list"),
    path("admin/penalties/new/", vadmin.PenaltyCreate.as_view(), name="penalty-create"),
    path("admin/penalties/<int:pk>/", vadmin.PenaltyUpdate.as_view(), name="penalty-update"),
    path("admin/penalties/ignored-modules/", vadmin.IgnoredModuleList.as_view(), name="ignored-modules"),
    path("admin/penalties/<int:pk>/delete/", vadmin.PenaltyDelete.as_view(), name="penalty-delete",),

    path("admin/rewards/", vadmin.RewardList.as_view(), name="reward-list"),
    path("admin/rewards/new/", vadmin.RewardCreate.as_view(), name="reward-create"),
    path("admin/rewards/<int:pk>/", vadmin.RewardUpdate.as_view(), name="reward-update"),
    path("admin/rewards/<int:pk>/delete/", vadmin.RewardDelete.as_view(), name="reward-delete",),


    # FC GUI
    path("fc/submit/", vfc.SubmissionCreateView.as_view(), name="submit"),
    path("fc/submissions/", vfc.MySubmissionsView.as_view(), name="my-submissions"),
    path("fc/submissions/<int:submission_id>/delete/", vfc.SubmissionDeleteView.as_view(), name="delete_submission",),
    path("systems/", vfc.SystemLookupView.as_view(), name="system-lookup"),

    # Review GUI
    path("review/", vrev.BatchListView.as_view(), name="review-list"),
    path("review/<int:submission_id>/", vrev.BatchDetailView.as_view(), name="review_detail"),
    path("review/<int:submission_id>/export/", vrev.ExportToCsvView.as_view(), name="export-srp"),
    path("review/<int:submission_id>/recheck/", vrev.RerunFitCheckView.as_view(), name="review-recheck"),
    path("review/<int:submission_id>/mode/toggle/", vrev.ToggleFitModeView.as_view(), name="review-toggle-mode"),
    path("review/<int:submission_id>/payouts/save/", vrev.SavePayoutsView.as_view(), name="review-save-payouts"),
    path("review/<int:submission_id>/kill/<int:kill_id>/delete/", vrev.ReviewKillDeleteView.as_view(), name="review-kill-delete"),
    path("review/<int:submission_id>/kill/add/", vrev.ReviewKillAddFromZkillView.as_view(), name="review-kill-add"),
    path("review/kills/<int:pk>/fit/", vrev.kill_fit_detail, name="kill-fit-detail"),
    path("review/<int:submission_id>/kill/<int:kill_id>/status/", vrev.SaveKillStatusView.as_view(), name="review-save-status"),

    # User Page
    path("me/", vuser.user_landing, name="user_landing"),

]
