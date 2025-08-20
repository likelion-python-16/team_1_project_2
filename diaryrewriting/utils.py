# diaryrewriting/utils.py
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model

USER_HEADER = "X-User-Id"
USER_COOKIE = "uid"

def get_or_create_user(req: HttpRequest):
    """
    - 로그인되어 있으면 User 반환
    - 헤더/쿠키의 uid로 조회되면 User 반환
    - 그 외(비로그인)면 공백 페이지('/')로 리다이렉트
    """
    User = get_user_model()

    # 1) 이미 인증된 사용자
    if getattr(req, "user", None) and req.user.is_authenticated:
        return req.user

    # 2) 헤더/쿠키 uid로 조회
    uid: Optional[str] = req.headers.get(USER_HEADER) or req.COOKIES.get(USER_COOKIE)
    if uid:
        try:
            return User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            pass

    # 3) 비로그인 → 공백 페이지로 리다이렉트
    return redirect("/")

def attach_uid_cookie(resp: HttpResponse, user) -> None:
    """
    User pk를 쿠키에 저장.
    """
    resp.set_cookie(
        USER_COOKIE,
        str(user.pk),
        httponly=False,
        samesite="Lax",
    )
