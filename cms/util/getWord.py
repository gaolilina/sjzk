from modellib.models.comboBox import ComboBox

def getDetail(id, hasId):
    '''获取该id的选项，返回（id）,value，child'''
    if id == None:
        return
    dict = {}
    combo = ComboBox.objects.filter(id = id)
    if combo:                                     #无此数据，返回
        combo = combo[0]
    else:
        return
    if hasId:
        dict['id'] = id
    dict['value'] = combo.value
    for child in combo.children.all():
        if 'child' not in dict:
            dict['child'] = []

        dict['child'].append(getDetail(child.id, hasId))

    return dict