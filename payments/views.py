import base64
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.serializers import RegisterSerializer

# Register API (JWT not required)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# User detail (for showing username)
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ModelSerializer  # 간단히 아래 override

    def get(self, request):
        return Response({"username": request.user.username})

# HTML pages
def register_page(request):
    return render(request, "register.html")

def login_page(request):
    return render(request, "login.html")

def payment_page(request):
    return render(request, "payment_page.html", {
        "order_name": "일일 다이어리",
        "amount": 10000,
        "toss_client_key": settings.TOSS_CLIENT_KEY,
    })
def success_page(request):
    return render(request, "success.html")

def fail_page(request):
    return render(request, "fail.html")

# Verify payment via Toss (requires JWT)
class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payment_key = request.data.get("paymentKey")
        if not payment_key:
            return Response({"detail": "paymentKey required"}, status=400)

        secret_key = settings.TOSS_SECRET_KEY
        if not secret_key:
            return Response({"detail": "TOSS_SECRET_KEY not configured"}, status=500)

        encoded = base64.b64encode(f"{secret_key}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }

        resp = requests.get(f"https://api.tosspayments.com/v1/payments/{payment_key}", headers=headers)
        data = resp.json()

        if resp.status_code != 200:
            return Response({"detail": "Toss lookup failed", "status": "ERROR"}, status=200)

        status_ = data.get("status")
        if status_ == "DONE":
            return Response({"detail": "검증 성공", "status": status_})
        else:
            # IN_PROGRESS 등도 200으로 내려줘서 클라이언트가 계속 폴링함
            return Response({"detail": "결제 진행 중", "status": status_})