from django.urls import path

from . import views

urlpatterns = [
    path("", views.search_view, name="search_view"),
    path("details/<str:symbol>/", views.fund_details_view, name="fund_details"),
]