import threading
import time


def get_class_functions(class_obj):
    # 提取class下全部函数及注释
    eval_globals = {'class_obj': class_obj}
    # 定义eval变量作用域
    return [{'function': i,
             'is_need_value': eval("class_obj.{}()[1]".format(i), eval_globals),
             'is_need_button': eval("class_obj.{}()[2]".format(i), eval_globals),
             'description': eval("class_obj.{}.__doc__".format(i), eval_globals)}
            for i in dir(class_obj) if "__" not in i]


def get_model_classes(model_obj):
    # 提取model下全部类名及注释
    eval_globals = {'model_obj': model_obj}
    # 定义eval变量作用域
    return [{'function': i, 'description': eval("model_obj.{}.__doc__".format(i), eval_globals)} for i in dir(model_obj) if "__" not in i]


def format_function_param(param):
    return param.replace('"', "'")


def exception_handle(exception_detail, step_name):
    # UI测试用例异常封装  错误截图
    if "TimeoutException" in exception_detail:
        raise SyntaxError("{}-查找元素超时\n错误详情:\n{}".format(step_name, exception_detail))
    elif "ElementNotVisibleException" in exception_detail:
        raise SyntaxError("{}-元素不可见\n错误详情:\n{}".format(step_name, exception_detail))
    elif "NoSuchAttributeException" in exception_detail:
        raise SyntaxError("{}-元素没有这个属性\n错误详情:\n{}".format(step_name, exception_detail))
    elif "NoAlertPresentException" in exception_detail:
        raise SyntaxError("{}-未找到alert弹出框\n错误详情:\n{}".format(step_name, exception_detail))
    elif "NoSuchFrameException" in exception_detail:
        raise SyntaxError("{}-未找到指定的iframe\n错误详情:\n{}".format(step_name, exception_detail))
    elif "UnexpectedAlertPresentException" in exception_detail:
        raise SyntaxError("{}-出现alert弹出框未处理\n错误详情:\n{}".format(step_name, exception_detail))
    elif "InvalidSwitchToTargetException" in exception_detail:
        raise SyntaxError("{}-切换到指定frame错误\n错误详情:\n{}".format(step_name, exception_detail))
    elif "UnexpectedTagNameException" in exception_detail:
        raise SyntaxError("{}-使用Tag Name不合法\n错误详情:\n{}".format(step_name, exception_detail))
    elif "StaleElementReferenceException" in exception_detail:
        raise SyntaxError("{}-陈旧元素引用异常\n错误详情:\n{}".format(step_name, exception_detail))
    elif "InvalidElementStateException" in exception_detail:
        raise SyntaxError("{}-元素状态异常 \n错误详情:\n{}".format(step_name, exception_detail))
    elif "ElementNotSelectableException" in exception_detail:
        raise SyntaxError("{}-元素不可被选中 \n错误详情:\n{}".format(step_name, exception_detail))
    elif "InvalidSelectorException" in exception_detail:
        raise SyntaxError("{}-定位元素语法错误 \n错误详情:\n{}".format(step_name, exception_detail))
    elif "AssertionError" in exception_detail:
        raise SyntaxError("{}-断言失败 \n错误详情:\n{}".format(step_name, exception_detail))
    elif "ElementClickInterceptedException" in exception_detail:
        raise SyntaxError("{}-元素点击失败(由于元素未加载/元素被遮挡) \n错误详情:\n{}".format(step_name, exception_detail))
    elif "chrome not reachable" in exception_detail:
        raise SyntaxError("{}-浏览器未正常关闭 \n错误详情:\n{}".format(step_name, exception_detail))

    # mysql错误捕获
    elif "1064" in exception_detail:
        raise SyntaxError("{}-sql语句语法错误\n错误详情:\n{}".format(step_name, exception_detail))
    elif "sql执行失败" in exception_detail:
        raise SyntaxError("{}-sql执行失败\n错误详情:\n{}".format(step_name, exception_detail))
    elif "2003" in exception_detail:
        raise SyntaxError("{}-数据库链接失败\n错误详情:\n{}".format(step_name, exception_detail))
    else:
        raise SyntaxError("{}-未捕获异常 \n错误详情:\n{}".format(step_name, exception_detail))


if __name__ == "__main__":

    from automatic_ui.common import selenium_functions
    # print(dir(selenium_functions))
    # print(selenium_functions.__name__)
    model_obj = selenium_functions
    for i in dir(selenium_functions):
        if "__" not in i:
            # print(selenium_functions, i)
            print("{}.{}.__doc__".format(str(selenium_functions.__name__), i))
            # print(eval("{}.{}.__doc__".format(str(selenium_functions.__name__.split(".")[-1]), i)))
            print(eval("model_obj.{}.__doc__".format(i)))

