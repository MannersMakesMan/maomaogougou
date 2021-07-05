

class execute_js_function:
    """执行原生js"""
    @classmethod
    def execute_js(cls, value=''):
        """执行原生js"""
        code = "self.driver.execute_script('{}')\n".format(value)
        is_need_value = 1
        # 是否需要输入参数
        is_need_button = 0
        # 是否需要定位
        return code, is_need_value, is_need_button


class click_function:
    """点击对象"""
    @classmethod
    def origin_click(cls, value=''):
        """原生selenium点击"""
        code = "temporary_button.click()\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def js_click(cls, value=''):
        """调用js点击"""
        code = "self.driver.execute_script('(arguments[0]).click()', temporary_button)\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button


class submit_function:
    """submit提交"""
    @classmethod
    def origin_submit(cls, value=''):
        code = "temporary_button.submit()\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button


class right_click_function:
    """鼠标右键单击"""
    @classmethod
    def origin_right_click(cls, value=''):
        """原生selenium点击"""
        code = "ActionChains(self.driver).context_click(temporary_button).perform()\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    # @classmethod
    # def js_click(cls):
    #     """调用js点击"""
    #     pass


# class click_hold_function:
#     """鼠标作键点击 不释放"""
#     @classmethod
#     def origin(cls):
#         """原生selenium点击"""
#         pass
#
#     @classmethod
#     def js_click(cls):
#         """调用js点击"""
#         pass


class send_key_function:
    """输入值"""
    @classmethod
    def origin_send_key(cls, value=''):
        """原生selenium输入 (只支持input元素)"""
        code = "temporary_button.send_keys('{}')\n".format(value)
        is_need_value = 1
        is_need_button = 1
        return code, is_need_value, is_need_button

    # @classmethod
    # def js(cls):
    #     """调用js输入 (只支持input元素)"""
    #     pass

    @classmethod
    def analog_keyboard_send_key(cls, value=''):
        """模拟键盘操作 (不需要定位元素 输入需要先点击输入框)"""
        code = "ActionChains(self.driver).send_keys('{}').perform()\n".format(value)
        is_need_value = 1
        is_need_button = 0
        return code, is_need_value, is_need_button


class mouse_hover_function:
    """鼠标悬停"""
    @classmethod
    def origin_click_mouse_hover(cls, value=''):
        """利用click点击进行鼠标悬停"""
        code = "temporary_button.click()\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def origin_mouse_hover(cls, value=''):
        """原生selenium悬停"""
        code = "ActionChains(self.driver).move_to_element(temporary_button).perform()\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def js_click_mouse_hover(cls, value=''):
        """使用js点击进行鼠标悬停"""
        code = "self.driver.execute_script('(arguments[0]).click()', temporary_button)\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button


class clear_function:
    """清空输入框"""
    @classmethod
    def origin_clear(cls, value=''):
        """原生selenium清空"""
        code = "temporary_button.clear()\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def js_clear(cls, value=''):
        """js方式清空"""
        code = "self.driver.execute_script('arguments[0].value = \"\";', temporary_button)\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button


    @classmethod
    def analog_keyboard_1(cls, value=''):
        """模拟键盘方式清空 Ctrl+A+Backspace (需要定位元素)"""
        code = "temporary_button.send_keys(Keys.CONTROL, 'a', Keys.BACK_SPACE)\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def analog_keyboard_2(cls, value=''):
        """模拟键盘方式清空 Ctrl+A+Backspace (不需要定位元素 需要提前点击元素)"""
        code = "ActionChains(self.driver).send_keys(Keys.CONTROL, 'a', Keys.BACK_SPACE).perform()\n"
        is_need_value = 0
        is_need_button = 0
        return code, is_need_value, is_need_button

    @classmethod
    def analog_keyboard_3(cls, value=''):
        """模拟键盘方式清空 Backspace*20 (需要定位元素)"""
        code = "[temporary_button.send_keys(Keys.BACK_SPACE) for _ in range(20)]\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def analog_keyboard_4(cls, value=''):
        """模拟键盘方式清空 Backspace*20 (不需要定位元素 需要提前点击元素)"""
        code = "[ActionChains(self.driver).send_keys(Keys.BACK_SPACE).perform() for _ in range(20)]\n"
        is_need_value = 0
        is_need_button = 0
        return code, is_need_value, is_need_button


class switch_iframe_function:
    """切换iframe"""
    @classmethod
    def into_iframe(cls, value=''):
        """进入iframe"""
        code = "self.driver.switch_to_frame(temporary_button)\n"
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def out_iframe(cls, value=''):
        """退出iframe"""
        code = "self.driver.switch_to.default_content()\n"
        is_need_value = 0
        is_need_button = 0
        return code, is_need_value, is_need_button


class forced_wait_function:
    """强制休眠"""
    @classmethod
    def origin_forced_wait(cls, value=''):
        """强制休眠"""
        code = "time.sleep(float('{}'))\n".format(value)
        is_need_value = 1
        is_need_button = 0
        return code, is_need_value, is_need_button


class alert_operate_function:
    """alert弹窗操作"""
    @classmethod
    def accept(cls, value=''):
        """点击 “确认”或“OK”"""
        code = "Alert(self.driver).accept()\n"
        is_need_value = 0
        is_need_button = 0
        return code, is_need_value, is_need_button

    @classmethod
    def dismiss(cls, value=''):
        """点击 “取消”或“Cancel”"""
        code = "Alert(self.driver).dismiss()\n"
        is_need_value = 0
        is_need_button = 0
        return code, is_need_value, is_need_button

    @classmethod
    def send_keys(cls, value=''):
        """发送文本，对有提交需求的prompt框"""
        code = "Alert(self.driver).send_keys('{}')\n".format(value)
        is_need_value = 1
        is_need_button = 0
        return code, is_need_value, is_need_button


class scrolling_pages_function:
    """滚动条操作"""
    @classmethod
    def roll_bottom(cls, value=''):
        """滑动到页面底部(纵向)"""
        code = "self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')\n"
        is_need_value = 0
        is_need_button = 0
        return code, is_need_value, is_need_button

    # @classmethod
    # def keyboard_roll(cls, value=''):
    #     """模拟键盘Down键滑动"""
    #     code = "ActionChains(driver).key_down(Keys.DOWN).perform()"
    #     is_need_value = 0
    #     is_need_button = 0
    #     return code, is_need_value, is_need_button

    @classmethod
    def scrollTop_roll(cls, value=''):
        """通过数值偏移值下拉(单位像素 纵向)"""
        code = "self.driver.execute_script('var q=document.documentElement.scrollTop={}')\n".format(value)
        is_need_value = 1
        is_need_button = 0
        return code, is_need_value, is_need_button

    @classmethod
    def horizontal_roll(cls, value=''):
        """拉到显示元素的位置(横向)"""
        code = "self.driver.execute_script('arguments[0].scrollIntoView();', temporary_button)\n".format(value)
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button


class assert_function:
    """断言"""
    @classmethod
    def equal_to(cls, element_attribute='', assert_value=''):
        """等于"""
        if element_attribute == 'text':
            code = "assert temporary_button.text == '{}'\n".format(assert_value)
        else:
            code = "assert temporary_button.get_attribute('{}') == '{}' if temporary_button.get_attribute('{}') else raise_exception(NoSuchAttributeException)\n".format(element_attribute, element_attribute, assert_value)
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def not_equal_to(cls, element_attribute='', assert_value=''):
        """不等于"""
        if element_attribute == 'text':
            code = "assert temporary_button.text != '{}'\n".format(assert_value)
        else:
            code = "assert temporary_button.get_attribute('{}') != '{}' if temporary_button.get_attribute('{}') else raise_exception(NoSuchAttributeException)\n".format(element_attribute, element_attribute, assert_value)
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button

    @classmethod
    def contain(cls, element_attribute='', assert_value=''):
        """包含(值包含于控件属性)"""
        if element_attribute == 'text':
            code = "assert '{}' in temporary_button.text\n".format(assert_value)
        else:
            code = "assert '{}' in temporary_button.get_attribute('{}') if temporary_button.get_attribute('{}') else raise_exception(NoSuchAttributeException)\n".format(element_attribute, element_attribute, assert_value)
        is_need_value = 0
        is_need_button = 1
        return code, is_need_value, is_need_button


class mysql_function:
    """执行sql"""
    @classmethod
    def exec_sql(cls, sql='', mysql_info=''):
        """执行sql"""
        code = 'mysql_operation.mysql_operation.exec_sql("{}", {})\n'.format(mysql_info, sql)
        is_need_value = 1
        is_need_button = 0
        return code, is_need_value, is_need_button


class drop_down_box_function:
    """下拉框数据选择"""
    @classmethod
    def select(cls, value=''):
        """ul/li类型下拉框选择 多选使用'//'分割"""
        code = 'select_ls="{}".split("//");[li.click() for li in temporary_button if li.text in select_ls]\n'.format(value)
        is_need_value = 1
        is_need_button = 1
        return code, is_need_value, is_need_button


if __name__ == "__main__":
    print(execute_js_function.execute_js.__str__())

