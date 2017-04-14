# coding:utf-8
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChuangYi.settings")

if django.VERSION >= (1, 7):  # 自动判断版本
    django.setup()


def add_illegal_word():
    """添加系统过滤词数据"""
    from main.models import IllegalWord
    filename = 'json_data/illegal_word.txt'
    # 读取过滤词文件中的数据并写入数据库
    with open(filename, 'r', encoding="utf-8") as f:
        for lines in f:
            word = lines.strip()
            if len(word) == 0:
                continue
            if len(word) > 20:
                word = word[:20]
            try:
                IllegalWord.objects.create(word=word)
            except:
                continue
        f.close()

if __name__ == "__main__":
    add_illegal_word()
