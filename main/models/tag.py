from django.db import models, transaction


class Tag(models.Model):
    """
    标签

    """
    name = models.CharField('名称', max_length=10, unique=True, db_index=True)

    class Meta:
        db_table = 'tag'

    @staticmethod
    def get(obj):
        """
        获取对象的标签列表

        """
        return [tag.name for tag in obj.tags.all().filter(is_enabled=True)]

    @staticmethod
    def set(obj, tag_list):
        """
        设置对象的标签列表

        :param obj: 带标签属性的对象
        :param tag_list: 标签名称列表

        """
        if len(tag_list) > 5:
            raise ValueError('too many tags')
        for i, name in enumerate(tag_list):
            name = name.strip().lower()
            if not name:
                raise ValueError('blank tag is not allowed')
            tag_list[i] = name

        tags = list(obj.tags.all())
        with transaction.atomic():
            # 设置标签
            for i, name in enumerate(tag_list):
                try:
                    tags[i].name = name
                    tags[i].is_enabled = True
                    tags[i].save(update_fields=['tag', 'is_enabled'])
                except IndexError:
                    obj.tags.create(order=i, name=name)
            # 将多余标签标记为无效
            i, j = len(tags), len(tag_list)
            if i > j:
                for t in tags[j:]:
                    t.is_enabled = False
                    t.save(update_fields=['is_enabled'])


class ObjectTag(models.Model):
    """
    对象标签基类

    """
    tag = models.ForeignKey(Tag, models.CASCADE, '+')
    order = models.IntegerField('序号')
    is_enabled = models.BooleanField('是否有效', default=True, db_index=True)

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
    user = models.ForeignKey('User', models.CASCADE, 'tags')

    class Meta:
        db_table = 'user_tag'


class TeamTag(ObjectTag):
    """
    团队标签

    """
    team = models.ForeignKey('Team', models.CASCADE, 'tags')

    class Meta:
        db_table = 'team_tag'
