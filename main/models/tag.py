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
        return [tag.name for tag in obj.tags.all()]

    @staticmethod
    def set(obj, tag_name_list):
        """
        设置对象的标签列表

        :param obj: 带标签属性的对象
        :param tag_name_list: 标签名称列表

        """
        if len(tag_name_list) > 5:
            raise ValueError('too many tags')
        for i, name in enumerate(tag_name_list):
            name = name.strip().lower()
            if not name:
                raise ValueError('blank tag is not allowed')
            tag_name_list[i] = name
        tags = obj.tags.all()
        with transaction.atomic():
            for i, name in enumerate(tag_name_list):
                try:
                    tags[i].name = name
                    tags[i].save(update_fields=['tag'])
                except IndexError:
                    obj.tags.create(order=i, name=name)


class ObjectTag(models.Model):
    """
    对象标签基类

    """
    tag = models.ForeignKey(Tag, models.CASCADE, '+')
    order = models.IntegerField('序号')

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
