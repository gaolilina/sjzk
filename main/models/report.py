from django.db import models
from django.utils import timezone


class Report(models.Model):
    """举报"""

    user = models.ForeignKey('User', models.CASCADE, 'reports')
    content = models.TextField(max_length=100)
    # 举报对象的类型:user、team、need、task、activity、competition、action、forum
    type = models.CharField(max_length=20, db_index=True)
    object_id = models.IntegerField(db_index=True)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'report'
