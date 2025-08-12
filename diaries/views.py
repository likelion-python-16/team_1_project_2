from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework import generics

from .models import DiaryEntry
from .serializers import DiaryEntrySerializer
from .permissions import IsOwnerOrReadOnly
from users.models import User
from summaries.models import DailySummary  # 감정 요약 모델
from summaries.serializers import DailySummarySerializer  # 감정 요약 시리얼라이저

class DiaryEntryViewSet(viewsets.ModelViewSet):
    """
    한줄일기 CRUD API
    
    list:
    로그인한 사용자 본인 일기 목록 조회 (최신순)
    
    retrieve:
    특정 일기 상세 조회
    
    create:
    새로운 일기 생성 (일일 작성 제한 및 프리미엄 체크 포함)
    
    update:
    일기 전체 수정
    
    partial_update:
    일기 부분 수정
    
    destroy:
    일기 삭제
    """
    serializer_class = DiaryEntrySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # 로그인한 사용자의 일기만 최신순으로 조회, 감정 요약(select_related) 포함
        return DiaryEntry.objects.filter(user=self.request.user).select_related('daily_summary').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        # 1. user_uuid 필수 확인
        user_uuid = request.data.get('user_uuid')
        if not user_uuid:
            return Response({"error": "user_uuid는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 유효한 사용자 존재 여부 확인
        try:
            user = User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            return Response({"error": "해당 UUID의 사용자가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 3. 일기 내용 유효성 확인
        content = request.data.get('text')  # 시리얼라이저에 맞게 'text'로 수정
        if not content or not content.strip():
            return Response({"error": "일기 내용은 비어 있을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. 하루 작성 제한 확인 (프리미엄 여부 반영)
        today = timezone.now().date()
        entry_count = DiaryEntry.objects.filter(user=user, created_at__date=today).count()

        if not getattr(user, 'is_premium', False) and entry_count >= 5:
            return Response({
                "detail": "오늘은 더 이상 일기를 작성할 수 없습니다. 프리미엄으로 업그레이드하면 더 많이 작성할 수 있어요."
            }, status=status.HTTP_403_FORBIDDEN)

        # 5. serializer를 사용해 저장 진행
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DiaryEntryCreateView(generics.CreateAPIView):
    queryset = DiaryEntry.objects.all()
    serializer_class = DiaryEntrySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_uuid = self.request.data.get('user_uuid')
        user = User.objects.get(uuid=user_uuid)  # 예외처리 필요
        serializer.save(user=user)