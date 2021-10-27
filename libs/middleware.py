from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .utils import json_response,get_request_real_ip
from account.models import User
import traceback
import time

class HandleExceptionMiddleware(MiddlewareMixin):
    """
    处理试图函数异常
    """
    def process_exception(self, request, exception):
        traceback.print_exc()
        return json_response(error='Exception: %s' % exception)

class AuthenticationMiddleware(MiddlewareMixin):
    """
    登录验证
    """
    def process_request(self, request):
        url = request.path
        if url != '/account/users/login/' and url != '/account/users/logout/':
            access_token = request.headers.get('x-token') or request.GET.get('x-token')
            if access_token and len(access_token) == 32:
                user = User.objects.filter(token=access_token).first()
                if user:
                    if user.token_expired >= time.time():
                        user.token_expired = time.time() + 30 * 60
                        user.save()
                        return None
                    else:
                        user.token_expired = 0
                        user.save()
                        response = json_response(message="登录过期，请重新登录。")
                        response.status_code = 401
                        return response
                else:
                    response = json_response(message="验证失败，请重新登录")
                    response.status_code = 401
                    return response
            else:
                response = json_response(message="无效登录，请重新登录")
                response.status_code = 401
                return response
        else:
            return None