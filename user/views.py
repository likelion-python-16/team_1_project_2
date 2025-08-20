import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login

def login_template(request):
    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize?"
        f"client_id={settings.KAKAO_REST_API_KEY}&"
        f"redirect_uri={settings.KAKAO_REDIRECT_URI}&"
        "response_type=code"
    )
    return render(request, 'login.html', {"kakao_auth_url": kakao_auth_url})

from django.contrib.auth import login

@csrf_exempt
def kakao_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect("/")

    # 1) 토큰 교환
    token_res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_res.raise_for_status()
    access_token = token_res.json().get("access_token")
    if not access_token:
        return redirect("/")

    # 2) 유저 정보
    user_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()

    kakao_id = user_info.get("id")
    profile = user_info.get("kakao_account", {}).get("profile", {}) or {}
    nickname = profile.get("nickname") or ""
    if not kakao_id:
        return redirect("/")

    # 3) 로컬 유저 연결/생성
    from django.contrib.auth.models import User
    username = f"kakao_{kakao_id}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": nickname[:30]},
    )
    if created:
        user.set_unusable_password()
        user.save()

    # 4) JWT 발급
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    refresh_str = str(refresh)

    # 5) 프론트로 안전하게 전달
    #   - 쿼리스트링은 서버 로그에 남으니 지양
    #   - 프래그먼트(#)는 서버로 전송되지 않음 → 프론트에서만 읽고 localStorage 저장
    redirect_url = f"http://localhost:3000/auth/callback#access={access}&refresh={refresh_str}"
    return redirect(redirect_url)

def profile_template(request):
    nickname = request.session.get("nickname")
    user_id = request.session.get("user_id")

    if not nickname:
        return render(request, 'profile.html', {"error": "로그인 정보가 없습니다."})

    return render(request, 'profile.html', {
        "nickname": nickname,
        "user_id": user_id,
    })

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        request.session.flush()  # 세션 초기화
        return redirect('/')
    return redirect('/')
