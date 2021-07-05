import re
import winrm


def getCaseMethods(caseFile):
    f = open(caseFile, 'r', encoding='utf-8')
    a = f.readlines()

    dict = {}
    for index in range(len(a)):
        value = a[index]
        if 'def' in value and 'test' in value:
            dict[value] = a[index+1]

    # a = dict
    return dict




def execute_run_all(id,methods):
    """
    0:未执行
    1:执行中
    2：执行成功
    3：执行失败
    :param id:
    :param methods:
    :return:
    """
    s = winrm.Session('http://192.168.13.105:5985/wsman', auth=('T1734', '123456'))
    try:
        r = s.run_cmd('cd {} && d: && python runAll_remote.py {}'.format("D:/GIT/Script/new_investment_trading_system","FundPosition-test_project_add--"))

        if 'success' in r.std_out:
            print('success')
        else:
            pass

        return 1
    except Exception as e:
        return 3
    # print('cd {} && d: && python runAll_remote.py {}'.format("D:GIT/Script/new_investment_trading_system","schemeSetting/test_position_plan_add-->schemeSetting/test_product_plan_delete-->"))

    # print(" bbbb")
