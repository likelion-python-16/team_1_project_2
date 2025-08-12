from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action

from .models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        # 관리자만 전체 조회 가능, 일반 사용자는 자기 자신만 보게 함
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(uuid=self.request.user.uuid)

    def retrieve(self, request, *args, **kwargs):
        # 일반 사용자라면 자기 자신만 조회 가능
        if not request.user.is_staff and str(request.user.uuid) != kwargs['pk']:
            return Response({'detail': '접근 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """현재 로그인한 사용자 정보 조회"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """닉네임 및 프리미엄 상태 업데이트"""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """자기 자신 탈퇴"""
        user = self.get_object()
        if request.user != user:
            return Response({'detail': '본인만 탈퇴 가능합니다.'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
