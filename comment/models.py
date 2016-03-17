from django.db import models
from django.utils import timezone

from activity.models import Activity
from project.models import Project
from team.models import Team
from user.models import User


class Comment(models.Model):
    author = None
    create_time = models.DateTimeField(
        '评论时间', default=timezone.now, db_index=True)
    content = models.TextField('评论内容', max_length=100, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-create_time']


class CommentOption(models.Model):
    allow_comment = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class UserComment(Comment):
    """
    对APP用户的评论

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'comments', 'comment',
        verbose_name='被评论用户')
    author = models.ForeignKey(
        User, models.CASCADE, 'comments_about_user', 'comment_about_user',
        verbose_name='评论者')

    class Meta:
        db_table = 'user_comment'

    def __repr__(self):
        return '<User Comment - %s / %s>' % (self.user.name, self.author.name)


class TeamComment(Comment):
    """
    对团队的评论

    """
    team = models.ForeignKey(
        Team, models.CASCADE, 'comments', 'comment',
        verbose_name='被评论团队')
    author = models.ForeignKey(
        User, models.CASCADE, 'comments_about_team', 'comment_about_team',
        verbose_name='评论者')

    class Meta:
        db_table = 'team_comment'

    def __repr__(self):
        return '<Team Comment - %s / %s>' % (self.team.name, self.author.name)


class ProjectComment(Comment):
    """
    对项目的评论

    """
    project = models.ForeignKey(
        Project, models.CASCADE, 'comments', 'comment',
        verbose_name='被评论项目')
    author = models.ForeignKey(
        User, models.CASCADE, 'comments_about_project', 'comment_about_project',
        verbose_name='评论者')

    class Meta:
        db_table = 'project_comment'

    def __repr__(self):
        return '<Project Comment - %s / %s>' % (
            self.project.name, self.author.name)


class ActivityComment(Comment):
    """
    对动态的评论

    """
    activity = models.ForeignKey(
        Activity, models.CASCADE, 'comments', 'comment',
        verbose_name='被评论动态')
    author = models.ForeignKey(
        User, models.CASCADE,
        'comments_about_activity', 'comment_about_activity',
        verbose_name='评论者')

    class Meta:
        db_table = 'activity_comment'

    def __repr__(self):
        return '<Activity Comment - %s / %s>' % (
            self.activity.id, self.author.name)


class UserCommentOption(CommentOption):
    """
    APP用户评论选项

    """
    user = models.OneToOneField(
        User, models.CASCADE, related_name='comment_option')

    class Meta:
        db_table = 'user_comment_option'

    def __repr__(self):
        return '<User Comment Option - %s>' % self.user.name


class TeamCommentOption(CommentOption):
    """
    团队评论选项

    """
    team = models.OneToOneField(
        Team, models.CASCADE, related_name='comment_option')

    class Meta:
        db_table = 'team_comment_option'

    def __repr__(self):
        return '<Team Comment Option - %s>' % self.team.name


class ProjectCommentOption(CommentOption):
    """
    项目评论选项

    """
    project = models.OneToOneField(
        Project, models.CASCADE, related_name='comment_option')

    class Meta:
        db_table = 'project_comment_option'

    def __repr__(self):
        return '<Project Comment Option - %s>' % self.project.name


class ActivityCommentOption(CommentOption):
    """
    动态评论选项

    """
    activity = models.OneToOneField(
        Activity, models.CASCADE, related_name='comment_option')

    class Meta:
        db_table = 'activity_comment_option'

    def __repr__(self):
        return '<Activity Comment Option - %s>' % self.activity.id
