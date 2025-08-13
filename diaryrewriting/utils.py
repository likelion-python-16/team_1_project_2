
from typing import Optional
from django.http import HttpRequest, HttpResponse
from .models import User

USER_HEADER = "X-User-Id"
USER_COOKIE = "uid"

def get_or_create_user(req: HttpRequest) -> User:
    uid: Optional[str] = req.headers.get(USER_HEADER) or req.COOKIES.get(USER_COOKIE)
    user = None
    if uid:
        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            user = None
    if user is None:
        user = User.objects.create()
    return user

def attach_uid_cookie(resp: HttpResponse, user: User) -> None:
    resp.set_cookie(USER_COOKIE, str(user.id), httponly=False, samesite="Lax")
