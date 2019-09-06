from modellib.models import Field
from util.base.view import BaseView


class FieldList(BaseView):

    def get(self, request, **kwargs):
        result = self.__format_child(None)
        return self.success(result)

    def __format_one_word(self, field):
        return {
            'name': field.name,
            'child': self.__format_child(field),
        }

    def __format_child(self, parent):
        fields = Field.objects.filter(parent=parent, enable=True)
        result = []
        for f in fields:
            result.append(self.__format_one_word(f))
        return result
