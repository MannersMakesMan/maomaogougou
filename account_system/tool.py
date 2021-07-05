from rest_framework.authtoken.models import Token

def get_real_name(request):

    token = request.META.get('HTTP_AUTHORIZATION')
    token_obj = Token.objects.get(key=token)
    real_name = token_obj.user.Real_name

    return real_name
