import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


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
        return redirect('/')

    # 1. 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code,
    }
    token_res = requests.post(token_url, data=token_data)
    access_token = token_res.json().get("access_token")

    # 2. 사용자 정보 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_res = requests.get(user_info_url, headers=headers)
    kakao_data = user_info_res.json()

    kakao_id = kakao_data.get("id")
    profile = kakao_data.get("kakao_account", {}).get("profile", {})
    nickname = profile.get("nickname", '')

    if not kakao_id or not nickname:
        return redirect('/')

    username = f'kakao_{kakao_id}'
    user, created = User.objects.get_or_create(username=username, defaults={'first_name': nickname})

    # 새로 만든 카카오 유저는 비밀번호 unusable 처리
    if created:
        user.set_unusable_password()
        user.save()

    # 🔹 장고 세션 로그인
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # (선택) 세션 변수에 추가 데이터 저장
    request.session['nickname'] = nickname

    return redirect('http://localhost:3000/')

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
    return redirect('/user/profile/')
