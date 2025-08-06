from rest_framework import viewsets, permissions
from .models import DailySummary
from .serializers import DailySummarySerializer

class DailySummaryViewSet(viewsets.ModelViewSet):
    """
    감정 요약 CRUD API
    
    list:
    모든 감정 요약 조회
    
    retrieve:
    특정 감정 요약 상세 조회
    
    create:
    새로운 감정 요약 생성
    
    update:
    감정 요약 전체 수정
    
    partial_update:
    감정 요약 부분 수정
    
    destroy:
    감정 요약 삭제
    """
    queryset = DailySummary.objects.all()
    serializer_class = DailySummarySerializer
    permission_classes = [permissions.IsAuthenticated]  # 로그인 사용자만 가능
