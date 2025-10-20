from django.urls import path
from . import views

app_name = "otp_auth"

urlpatterns = [
    path("login/", views.send_otp_view, name="send_otp"),
    path("verify/", views.verify_otp_view, name="verify_otp"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]
