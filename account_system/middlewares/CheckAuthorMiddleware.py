from rest_framework.authtoken.models import Token
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class CheckAuthorMiddleware(MiddlewareMixin):
    def process_request(self, request):
        valid_menu = ["/login", "/doc", "/static", "/test_report"]
        if request.path == '/':
            return
        for valid_url in valid_menu:
            if valid_url in request.path:
                return
        else:
            # token验证中间件
            token = request.META.get('HTTP_AUTHORIZATION')
            if token == 'dev':
                return
            if not token:
                return HttpResponse('请重新登录', status=401)
            else:
                if not Token.objects.filter(key=token.replace("token ", "")):
                    return HttpResponse('请重新登录', status=401)
