from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.conf import settings
import requests
from .settings import OTP_API_BASE, OTP_API_KEY


# -------------------------------
# Step 1: Send OTP
# -------------------------------
def send_otp_view(request):
    if request.method == "POST":
        mobile = request.POST.get("mobile")

        if not mobile:
            messages.error(request, "Please enter a valid mobile number.")
            return redirect("otp_auth:send_otp")

        try:
            payload = {"mobile_number": mobile}
            headers = {"X-API-KEY": OTP_API_KEY}

            response = requests.post(f"{OTP_API_BASE}/generate/", json=payload, headers=headers, timeout=10)
            data = response.json()

            if response.status_code == 201:
                request.session["mobile"] = mobile
                request.session["session_id"] = data.get("session_id")
                messages.success(request, "OTP sent successfully!")
                return redirect("otp_auth:verify_otp")
            else:
                messages.error(request, data.get("detail", "Failed to send OTP"))

        except requests.exceptions.RequestException as e:
            messages.error(request, f"OTP service unreachable: {e}")

    return render(request, "otp_auth/login.html")


# -------------------------------
# Step 2: Verify OTP
# -------------------------------
def verify_otp_view(request):
    mobile = request.session.get("mobile")
    session_id = request.session.get("session_id")

    if not mobile or not session_id:
        messages.error(request, "Session expired. Please try again.")
        return redirect("otp_auth:send_otp")

    if request.method == "POST":
        otp_code = request.POST.get("otp")

        if not otp_code:
            messages.error(request, "Please enter OTP.")
            return redirect("otp_auth:verify_otp")

        try:
            payload = {"session_id": session_id, "otp_code": otp_code}
            headers = {"X-API-KEY": OTP_API_KEY}
            response = requests.post(f"{OTP_API_BASE}/verify/", json=payload, headers=headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("detail") == "OTP verified successfully":
                user, _ = User.objects.get_or_create(username=mobile)
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("otp_auth:dashboard")

            messages.error(request, data.get("detail", "Invalid OTP"))

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Verification error: {e}")

    return render(request, "otp_auth/verify.html", {"mobile": mobile})


# -------------------------------
# Dashboard
# -------------------------------
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("otp_auth:send_otp")
    return render(request, "otp_auth/dashboard.html", {"user": request.user})


# -------------------------------
# Logout
# -------------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("otp_auth:send_otp")
