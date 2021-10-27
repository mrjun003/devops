import uuid
from libs.parser import JsonParser, Argument
from libs.utils import json_response,human_datetime
from .models import *
import time

# Create your views here.
def login(request):
    form, error = JsonParser(
        Argument('username', help='请输入用户名'),
        Argument('password', help='请输入密码')
    ).parse(request.body)
    if error is None:
        user = User.objects.filter(name=form.username).first()
        if user:
            if user.is_active == 0:
                return json_response(message="帐号未激活，请联系管理员！")
            if user.verify_password(form.password):
                return json_response(message="密码错误")
        else:
            return json_response(message="帐号不存在")
        user.token=uuid.uuid4().hex
        user.token_expired = time.time() + 8 * 60 * 60
        user.last_login_time = human_datetime()
        user.save()
        return json_response({
            'token': user.token,
            'username':user.name,
            'permissions': user.get_permission
        })
    else:
        return json_response(message=error)


def logout(request):
    access_token = request.headers.get('x-token') or request.GET.get('x-token')
    user = User.objects.filter(token=access_token).first()
    if user:
        user.token_expired = 0
        user.token = ''
        user.save()
        return json_response()
    else:
        response = json_response(message="无效登录，请重新登录")
        response.status_code = 401
        return response

