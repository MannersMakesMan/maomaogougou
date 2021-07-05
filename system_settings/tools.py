from django.http import JsonResponse


def error_response(msg):
    return JsonResponse(data={
        'data': '',
        'msg': msg,
        'code': '999998'
    })


def success_response(msg, data=None):
    return JsonResponse(data={
        'data': data if data else '',
        'msg': msg if msg else '',
        'code': '999999'
    })