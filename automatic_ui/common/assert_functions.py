
class assert_location:
    """断言验证"""
    @classmethod
    def is_exist_location(cls):
        """校验 页面是否存在元素"""
        code = "assert temporary_button != []"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

