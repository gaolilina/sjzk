from django.db import models, transaction


class Tag(models.Model):
    """
    标签

    """
    name = models.CharField('名称', max_length=10, unique=True, db_index=True)

    class Meta:
        db_table = 'tag'


class ObjectTagManager(models.Manager):
    def get_tags(self, obj):
        """
        获取对象的标签列表

        """
        qs = self.filter(object=obj, is_enabled=True)

        return [tag.name for tag in qs] if qs else [None]

    def set_tags(self, obj, tags):
        """
        设置对象的标签列表

        :param obj: 带标签属性的对象
        :param tags: 标签名称列表

        """
        if len(tags) > 5:
            raise ValueError('too many tags')
        for i, name in enumerate(tags):
            name = name.strip().lower()
            if not name:
                raise ValueError('blank tag is not allowed')
            tags[i] = name

        old_tags = list(self.filter(object=obj).all())
        with transaction.atomic():
            # 设置标签
            for i, name in enumerate(tags):
                try:
                    old_tags[i].name = name
                    old_tags[i].is_enabled = True
                    old_tags[i].save(update_fields=['tag', 'is_enabled'])
                except IndexError:
                    self.create(object=obj, order=i, name=name)
            # 将多余标签标记为无效
            i, j = len(old_tags), len(tags)
            if i > j:
                for t in old_tags[j:]:
                    t.is_enabled = False
                    t.save(update_fields=['is_enabled'])


class ObjectTag(models.Model):
    """
    对象标签基类

    """
    object = None
    tag = models.ForeignKey(Tag, models.CASCADE, '+')
    order = models.IntegerField('序号')
    is_enabled = models.BooleanField('是否有效', default=True, db_index=True)

    objects = ObjectTagManager()

    class Meta:
        abstract = True
        ordering = ['order']

    @property
    def name(self):
        """
        获取记录对应标签的标签名称

        """
        return self.tag.name

    @name.setter
    def name(self, tag_name):
        """
        根据标签名称设置记录的标签外键

        """
        tag, created = Tag.objects.get_or_create(name=tag_name)
        self.tag = tag


class UserTag(ObjectTag):
    """
    用户标签

    """
    object = models.ForeignKey('User', models.CASCADE, 'tags')

    class Meta:
        db_table = 'user_tag'


class TeamTag(ObjectTag):
    """
    团队标签

    """
    object = models.ForeignKey('Team', models.CASCADE, 'tags')

    class Meta:
        db_table = 'team_tag'
