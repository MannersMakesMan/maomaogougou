# from rest_framework.views import APIView
# from rest_framework.authentication import TokenAuthentication
# from asset_information.models import Server
# from automated_testing.common.api_response import JsonResponse
#
# class ServerLevelTreeView(APIView):
#     """
#     服务器 虚拟机 服务 层级菜单结构
#
#     [
#
#      id:1,
#      label:’serverName‘,
#      children:[
#      [id:2,label:'vmserver1',children:[
#      [id:5,label:'serviceName'],[]
#
#      ]],
#     [id:2,label:'vmserver1',]
#
#      ]
#
#
#     ]
#     """
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = []
#
#     def get(self, request):
#         res_data = []
#         servers = Server.objects.all()
#         for server in servers:
#             server_data = {'label': server.ipaddress, 'id': server.id}
#             vm_servers = server.server.all()  # 根据外键正向取数据
#             if vm_servers:
#                 server_data['children'] = []
#                 index = 0
#                 for vm_server in vm_servers:
#                     server_data['children'].append(
#                         {'label': vm_server.name, "id": vm_server.id})
#                     services = vm_server.vm_server.all()
#                     if services:
#                         server_data['children'][index]['children'] = []
#                         for service in services:
#                             server_data['children'][index]['children'].append(
#                                 {'label': service.name, 'id': service.id})
#                         index += 1
#
#             res_data.append(server_data)
#
#         return JsonResponse(data=res_data, code='999999', msg='成功!')
