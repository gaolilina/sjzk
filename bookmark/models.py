from django.db import models
from django.utils import timezone

from activity.models import Activity
from user.models import User


class ActivityBookmarker(models.Model):
    """
    动态收藏者记录

    """
    activity = models.ForeignKey(
        Activity, models.CASCADE, related_name='bookmarker_info')
    user = models.ForeignKey(
        User, models.CASCADE, related_name='bookmarked_activity_info')
    create_time = models.DateTimeField('收藏时间', default=timezone.now)

    class Meta:
        db_table = 'activity_bookmarker'
        ordering = ['-create_time']

    def __repr__(self):
        return '<Activity Bookmarker - %s / %s>' % (
            self.liked.id, self.liker.name)
