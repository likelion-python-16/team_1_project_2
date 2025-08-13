
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DiaryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('emotion', models.CharField(max_length=50, null=True, blank=True)),
                ('lat', models.FloatField(null=True, blank=True)),
                ('lng', models.FloatField(null=True, blank=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='entries', to='diaryrewriting.user')),
            ],
            options={'ordering': ['-timestamp']},
        ),
        migrations.CreateModel(
            name='DailySummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('summary_text', models.TextField(blank=True)),
                ('emotion', models.CharField(max_length=50, blank=True)),
                ('recommended_items', models.JSONField(null=True, blank=True)),
                ('diary_text', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='summaries', to='diaryrewriting.user')),
            ],
            options={'ordering': ['-date'], 'unique_together': {('user', 'date')}},
        ),
    ]
