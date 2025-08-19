# diaryrewriting/utils.py
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model

USER_HEADER = "X-User-Id"
USER_COOKIE = "uid"

def get_or_create_user(req: HttpRequest):
    """
    - 우선 요청 헤더나 쿠키에서 유저 id(pk)를 찾는다.
    - 존재하면 User 조회, 없으면 새 User 생성.
    """
    User = get_user_model()
    uid: Optional[str] = req.headers.get(USER_HEADER) or req.COOKIES.get(USER_COOKIE)
    user = None
    if uid:
        try:
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            user = None

    if user is None:
        # 기본 User 모델에 맞게 최소 username은 넣어야 함
        user = User.objects.create(username=f"guest_{User.objects.count()+1}")
        user.set_unusable_password()
        user.save()
    return user


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
