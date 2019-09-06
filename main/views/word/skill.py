from modellib.models import Skill
from util.base.view import BaseView


class SkillList(BaseView):

    def get(self, request, **kwargs):
        result = self.__format_child(None)
        return self.success(result)

    def __format_one_word(self, skill):
        return {
            'name': skill.name,
            'child': self.__format_child(skill),
        }

    def __format_child(self, parent):
        skills = Skill.objects.filter(parent=parent, enable=True)
        result = []
        for f in skills:
            result.append(self.__format_one_word(f))
        return result
