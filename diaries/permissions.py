from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    오직 작성자(Owner)만 수정, 삭제 가능.
    읽기는 모두 허용.
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청(GET, HEAD, OPTIONS)은 모두 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 작성자(user)와 요청 user가 같은지 검사
        return obj.user.uuid == request.user.uuid
