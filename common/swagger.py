from drf_yasg2.generators import OpenAPISchemaGenerator
from drf_yasg2.inspectors import SwaggerAutoSchema

class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    """重写 SwaggerAutoSchema 自定义接口分类"""
    def get_tags(self, operation_keys=None):
        # swagger 接口氛组
        # 使用app的分组
        tags = super().get_tags(operation_keys)

        # 使用url分组
        # url = ''
        # url = operation_keys[-1]
        # if url in operation_keys:
        #     #  `operation_keys` 内容像这样 ['v1', 'prize_join_log', 'create']
        #     tags[0] = operation_keys[1]

        return tags

class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """重写 OpenAPISchemaGenerator 实现每个tag的说明文本"""

    def get_schema(self, request=None, public=False):
        swagger = super().get_schema(request, public)
        # 定义每个分类的说明
        swagger.tags = [
            {
                "name": "Operation_maintenance",
                "description": "UI&API自动化 文件操作模块",
            },
            {
                "name": "TestExeConf",
                "description": "UI&API自动化 配置执行操作模块",
            },
            {
                "name": "account_system",
                "description": "用户&权限&部门模块",
            },
            {
                "name": "asset_information",
                "description": "资产管理模块",
            },
            {
                "name": "SystemManage",
                "description": "系统管理模块",
            },
            {
                "name": "zyApiTest",
                "description": "v-0.2 API自动化测试模块",
            },
            {
                "name": "UiTest",
                "description": "UI自动化测试模块",
            }
        ]

        return swagger
