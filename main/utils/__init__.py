import os

from PIL import Image
from django.utils import timezone

from ChuangYi.settings import UPLOADED_URL
from .abort import abort
from .http import send_message, identity_verify, picture_verify

__all__ = ['abort', 'send_message', 'identity_verify', 'picture_verify',
           'save_uploaded_image']


def save_uploaded_image(image, is_private=False):
    """保存上传的图片，返回其相对路径"""
    code = picture_verify(image)
    if code and code != 0:
        abort(403, 'unhealthy picture')
    now = timezone.now()
    dirname = UPLOADED_URL + now.strftime('%Y/%m/%d')
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
