from django.urls import path, re_path
from reservations import views
from reservations.api import views as api_views

urlpatterns = [
    re_path(r"^$", views.dashboard, name="dashboard"),
    re_path(r"^accounts/logout/$", views.logout_user, name="logout"),

    # General Views
    re_path(r"^new/$", views.new_reservation, name="new_reservation"),
    re_path(r"^(?P<reservation_id>[0-9]+)/$", views.reservation, name="reservation"),
    re_path(r"^(?P<reservation_id>[0-9]+)/delete/$", views.delete_reservation, name="delete_reservation"),
    re_path(r"^(?P<reservation_id>[0-9]+)/edit/$", views.edit_reservation, name="edit_reservation"),

    re_path(r"^tournament/(?P<tournament_id>[0-9]+)/$", views.tournament, name="tournament"),

    re_path(r"^editor/1/$", views.editor_step1, name="editor_step1"),
    re_path(r"^editor/2/$", views.editor_step2, name="editor_step2"),
    re_path(r"^editor/3/$", views.editor_step3, name="editor_step3"),
    re_path(r"^editor/complete/$", views.editor_complete, name="editor_complete"),

    re_path(r"^mine/$", views.my_reservations, name="my_reservations"),
    re_path(r"^account/$", views.account, name="account"),
    re_path(r"^accounts/change-email/$", views.change_email, name="change_email"),
    re_path(r"^accounts/change-password/$", views.change_password, name="change_password"),
    re_path(r"^csv/$", views.get_csv, name="get_csv"),
    re_path(r"^recovery/(?P<reservation_id>[0-9]+)/$", views.recovery_reservation, name="recovery_reservation"),

    # Admin Views
    re_path(r"^admin/$", views.all_reservations, name="all_reservations"),
    re_path(r"^admin/old/$", views.old_reservations, name="old_reservations"),
    re_path(r"^admin/swap/$", views.swap_reservations, name="swap_reservations"),
    re_path(r"^admin/(?P<reservation_id>[0-9]+)/approve/$", views.approve_reservation, name="approve_reservation"),

    re_path(r"^admin/recovery/$", views.recovery, name="recovery"),
    re_path(r"^admin/recovery/f/(?P<field_id>[0-9]+)/$", views.recovery, name="recovery_field"),
    re_path(r"^admin/recovery/t/(?P<tournament_id>[0-9]+)/$", views.recovery, name="recovery_tournament"),
    re_path(r"^admin/recovery/g/(?P<gametype_id>[0-9]+)/$", views.recovery, name="recovery_gametype"),
    re_path(r"^admin/recovery/tm/(?P<team_id>[0-9]+)/$", views.recovery, name="recovery_team"),

    re_path(r"^admin/fields/$", views.all_fields, name="all_fields"),
    re_path(r"^admin/fields/add/$", views.add_field, name="add_field"),
    re_path(r"^admin/fields/(?P<field_id>[0-9]+)/$", views.field, name="field"),
    re_path(r"^admin/fields/(?P<field_id>[0-9]+)/change/$", views.change_field_name, name="change_field_name"),
    re_path(r"^admin/fields/(?P<field_id>[0-9]+)/delete/$", views.delete_field, name="delete_field"),
    re_path(r"^admin/fields/(?P<field_id>[0-9]+)/addTime/$", views.field_add_timeslot, name="field_add_timeslot"),
    re_path(r"^admin/fields/(?P<field_id>[0-9]+)/removeTime/(?P<timeslot_id>[0-9]+)/$", views.field_remove_timeslot, name="field_remove_timeslot"),

    re_path(r"^admin/teams/$", views.all_teams, name="all_teams"),
    re_path(r"^admin/teams/new/$", views.new_team, name="new_team"),
    re_path(r"^admin/teams/(?P<team_id>[0-9]+)/edit/$", views.edit_team, name="edit_team"),
    re_path(r"^admin/teams/(?P<team_id>[0-9]+)/delete/$", views.delete_team, name="delete_team"),

    re_path(r"^admin/tournaments/$", views.all_tournaments, name="all_tournaments"),
    re_path(r"^admin/tournaments/new/$", views.new_tournament, name="new_tournament"),
    re_path(r"^admin/tournaments/(?P<tournament_id>[0-9]+)/edit/$", views.edit_tournament, name="edit_tournament"),
    re_path(r"^admin/tournaments/(?P<tournament_id>[0-9]+)/delete/$", views.delete_tournament, name="delete_tournament"),

    re_path(r"^admin/gametypes/$", views.all_gametypes, name="all_gametypes"),
    re_path(r"^admin/gametypes/new/$", views.new_gametype, name="new_gametype"),
    re_path(r"^admin/gametypes/(?P<gametype_id>[0-9]+)/delete$", views.delete_gametype, name="delete_gametype"),

    re_path(r"^admin/managers/$", views.all_managers, name="all_managers"),
    re_path(r"^admin/managers/(?P<user_id>[0-9]+)/remove/manager/$", views.remove_manager, name="remove_manager"),
    re_path(r"^admin/managers/(?P<user_id>[0-9]+)/remove/superuser/$", views.remove_superuser, name="remove_superuser"),
    re_path(r"^admin/managers/new/superuser/$", views.new_superuser, name="new_superuser"),
    re_path(r"^admin/managers/new/manager/$", views.new_manager, name="new_manager"),

    re_path(r"^admin/settings/$", views.website_settings, name="website_settings"),
    re_path(r"^admin/settings/editCalendar/$", views.edit_calendar, name="edit_calendar"),
    re_path(r"^admin/settings/editTimeout/$", views.edit_timeout, name="edit_timeout"),
    re_path(r"^admin/settings/editBlockTime/$", views.edit_block_time, name="edit_block_time"),
    re_path(r"^admin/settings/refreshTokens/$", views.refresh_tokens, name="refresh_tokens"),
    re_path(r"^admin/settings/editSiteConfig/$", views.edit_site_config, name="edit_site_config"),

    # API Views
    re_path(r"^api/modifyFields/$", api_views.APITeamModifyFields.as_view(), name="api_team_modify_fields"),
    re_path(r"^api/modifyTeams/$", api_views.APIFieldModifyTeams.as_view(), name="api_field_modify_teams"),
    re_path(r"^api/modifyManagers/$", api_views.APIManagerModifyTeams.as_view(), name="api_manager_modify_teams"),
    re_path(r"^api/reservation/$", api_views.APIReservationList.as_view(), name="api_reservation_list"),
    re_path(r"^api/reservation/(?P<pk>[0-9]+)/$", api_views.APIReservationDetail.as_view(), name="api_reservation_detail"),
    re_path(r"^api/tournament/$", api_views.APITournamentList.as_view(), name="api_tournament_list"),
    re_path(r"^api/tournament/(?P<pk>[0-9]+)/$", api_views.APITournamentDetail.as_view(), name="api_tournament_detail"),
    re_path(r"^api/team/$", api_views.APITeamList.as_view(), name="api_team_list"),
    re_path(r"^api/team/(?P<pk>[0-9]+)/$", api_views.APITeamDetail.as_view(), name="api_team_detail"),
    re_path(r"^api/toggleSidebar/$", api_views.APIToggleSidebar.as_view(), name="api_toggle_sidebar"),
    re_path(r"^api/clearTokens/$", api_views.APIClearTokens.as_view(), name="api_clear_tokens"),
]
