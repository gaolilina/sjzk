# 第一句话一定要引入这个，不能没有
import recommend

# 具体计算
from main.models import User
import pandas as pd
from sklearn.cluster import KMeans

# 权重
WEIGHTS_SIM1 = 0.2
WEIGHTS_SIM2 = 0.8

# 统计的字段
USER_PARAM_LIST = ['province', 'city', 'role', 'adept_field', 'profession']

# 相似度结果
result_user_sim = None


def user_sim():
    # 聚类
    result_cluster = dataframe()
    # 计算相似度
    global result_user_sim
    result_user_sim = sim(result_cluster)
    return result_user_sim


def sim1(u1, u2, result_cluster):
    if result_cluster[u1.id] == result_cluster[u2.id]:
        return 1
    else:
        return 0


'''
提取某两个用户的所有朋友，计算这两个用户间的相似度，原理是共同的朋友越多，认为两个人越相似。
计算方法是余弦公式
'''


def sim2(u1, u2):
    # friends_u1 是 u1 的好友的 id 的集合
    friends_u1 = [f[0] for f in u1.friends.all().values_list('other_user')]
    if len(friends_u1) == 0:
        return 0
    # part1 是两个向量的点积
    part1 = u2.friends.filter(other_user_id__in=friends_u1).count()
    if part1 == 0:
        return 0
    # part2 是两个向量的模积
    part2 = len(friends_u1) * u2.friends.count()
    if part2 == 0:
        return 0
    return part1 / part2


def dataframe():
    qs = get_user().values_list(*USER_PARAM_LIST, 'id')
    len_qs = len(qs)
    if len_qs < 1:
        return []
    # 构造原始数据
    origin_data = {}
    len_param = len(USER_PARAM_LIST)
    for i in range(0, len_param):
        origin_data[USER_PARAM_LIST[i]] = []
    for u in qs:
        for i in range(0, len_param):
            d = u[i]
            origin_data[USER_PARAM_LIST[i]].append(d if d else '无')
    # 聚类
    df = pd.DataFrame(origin_data)
    dummies = pd.get_dummies(df, columns=USER_PARAM_LIST)
    result_tmp = KMeans(n_clusters=10, random_state=9).fit_predict(dummies)
    # 将结果规整化，返回一个数组，数组的 index 是用户 id，value 是分类
    result = []
    next_index = 0
    for i in range(0, qs[len_qs - 1][len_param] + 1):
        next_user_id = qs[next_index][len_param]
        if next_user_id == i:
            result.append(result_tmp[next_index])
            next_index += 1
        else:
            result.append(None)
    return result


def sim(result_cluster):
    users = get_user()
    result = dict()
    for u1 in users:
        id_u1 = u1.id
        for u2 in users:
            id_u2 = u2.id
            # 只用计算一半，因为 u1 和 u2 的相似度，与 u2 和 u1 的一样
            if id_u2 >= id_u1:
                continue
            key = (id_u1, id_u2)
            value = WEIGHTS_SIM1 * sim1(u1, u2, result_cluster) + WEIGHTS_SIM2 * sim2(u1, u2)
            result[key] = value
    return result


def get_user():
    return User.objects.all().order_by('id')


def sort(users, current):
    global result_user_sim
    if result_user_sim is None or current is None or len(users) < 2:
        return users
    users.sort(key=lambda u: sort_single(u['id'], current.id))
    return users


def sort_single(id_u1, id_u2):
    if id_u1 == id_u2:
        return 1
    key = (id_u1, id_u2) if id_u1 > id_u2 else (id_u2, id_u1)
    global result_user_sim
    result_sim = result_user_sim.get(key)
    return result_sim if result_sim else 0
