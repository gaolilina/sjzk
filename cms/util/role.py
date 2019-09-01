from modellib.models import CMSRole


def compare_role(high, low):
    '''
    角色 high 是否比 low 角色等级高
    :param high:
    :param low:
    :return:
    '''
    if high is None:
        return False
    if low is None:
        return True
    # 向上递归找，被操作角色是不是操作者角色的子孙
    while low is not None:
        # 先判断级别，限制同级或越级修改（也包括超管的权限不允许被修改
        if high.level >= low.level:
            return False
        # 判断父子关系
        if low.parent_role == high:
            return True
        low = low.parent_role
    return False


def get_all_child_role(role, **filter_param):
    """获取一个角色的所有子角色，递归获取"""
    if role is None:
        return []
    if role.is_admin():
        return CMSRole.objects.exclude(parent_role__isnull=True).filter(**filter_param)
    role_list = [role]
    # 递归获取
    for r in role_list:
        role_list.extend(r.child_roles.filter(**filter_param))
    role_list.remove(role)
    return role_list


def role_to_json(r):
    return {
        'id': r.id,
        'name': r.name,
        'enable': r.enable,
        'category': r.category
    }
