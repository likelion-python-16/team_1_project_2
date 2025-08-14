from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import EmotionDiary, DiaryRecord
from .serializers import EmotionDiarySerializer, DiaryRecordSerializer


class EmotionDiaryViewSet(viewsets.ModelViewSet):
    queryset = EmotionDiary.objects.all().order_by('-date')
    serializer_class = EmotionDiarySerializer


class DiaryRecordViewSet(viewsets.ModelViewSet):
    queryset = DiaryRecord.objects.all().order_by('-time')
    serializer_class = DiaryRecordSerializer

def summary_page(request):
    # 가장 최근 데이터 1건만 불러오기
    diary = EmotionDiary.objects.order_by('-date').first()
    records = DiaryRecord.objects.all().order_by('time')  # 시간 순 정렬

    return render(request, 'summary.html', {
        'diary': diary,
        'records': records
    })