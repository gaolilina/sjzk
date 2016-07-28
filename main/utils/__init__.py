import os

from PIL import Image
from django.utils import timezone

from .abort import abort


__all__ = ['abort', 'save_uploaded_image']


def save_uploaded_image(image, is_private=False):
    """保存上传的图片，返回其相对路径"""

    now = timezone.now()
    dirname = now.strftime('%Y/%m/%d')
    if is_private:
        dirname = 'private/' + dirname
    os.makedirs(dirname, exist_ok=True)

    filename = dirname + now.strftime('%H%M%S%f') + '.jpg'
    try:
        with Image.open(image) as i:
            i.save(filename, quality=90)
    except IOError:
        return None
    else:
        return filename
