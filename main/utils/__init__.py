import os

from PIL import Image
from django.utils import timezone

from .abort import abort
from .http import send_message, identity_verify, picture_verify, eid_verify
from .system import get_score_stage

__all__ = ['abort', 'send_message', 'identity_verify', 'picture_verify',
           'save_uploaded_image', 'get_score_stage', 'save_uploaded_file',
           'eid_verify']


def save_uploaded_image(image, is_private=False):
    """保存上传的图片，返回其相对路径"""
    code = picture_verify(image)
    if code and code != 0:
        abort(403, 'unhealthy picture')
    now = timezone.now()
    if is_private:
        dirname = "uploaded/" + "private/" + now.strftime('%Y/%m/%d')
    else:
        dirname = "uploaded/" + now.strftime('%Y/%m/%d')
    os.makedirs(dirname, exist_ok=True)

    filename = dirname + now.strftime('%H%M%S%f') + '.jpg'
    try:
        with Image.open(image) as i:
            i.save(filename, quality=90)
    except IOError:
        return None
    else:
        return filename


def save_uploaded_file(file, object_id, status, other_id):
    dirname = "uploaded/competition/" + str(object_id) + "/" + str(status)\
              + "/" + str(other_id)
    os.makedirs(dirname, exist_ok=True)

    filename = dirname + "/" + file.name
    try:
        destination = open(filename, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
    except IOError:
        return None
    else:
        return filename
