import json

from automatic_ui.ui_script_execution import ui_script_execution
from system_settings.models import TaskControl, MysqlInfo
from system_settings.tools import error_response
from test_exe_conf.serializers import ApiTestReportSerializers
from user_interface_test_code.models import TestCaseData, UiTestScene, CommonParams, UiSceneTestCaseIndex, UiSceneParams
from user_interface_test_code.serializers import TestCaseDataSerializerQuery
from zy_api_testing.tools import send_emails


def get_one_test_case_data(test_case_ids, environment_ip, explicit_wait_timeout, explicit_wait_poll_time, implicitly_wait_timeout, remote_ip):
    """
    获取单个测试用例执行数据
    """
    step_data_list = []
    for test_case_id in test_case_ids:
        step_obj_list = TestCaseData.objects.filter(test_case_id=int(test_case_id)).order_by('sort')
        step_data_obj_list = TestCaseDataSerializerQuery(step_obj_list, many=True)
        step_data_list += step_data_obj_list.data

    test_case_data = []
    step_list = []
    for step_data in step_data_list:
        item = {}
        item['function'] = step_data.get('operate_func')
        item['ele_attribute'] = step_data.get('ele_attribute', '')
        item['assert_value'] = step_data.get('assert_value', '')
        item['step_desc'] = step_data.get('step_desc', '')
        try:
            item['function_method'] = step_data.get('action_func')
        except Exception as e:
            pass
        item['location'] = step_data.get('location_func')
        item['location_param'] = step_data.get('location_value')
        if step_data.get('func_common_param_id', None):
            item['value'] = CommonParams.objects.get(id=step_data['func_common_param_id']).param_value
        else:
            item['value'] = step_data.get('func_param', '')
        if step_data.get('mysql_info_id', None):
            mysql_info_obj = MysqlInfo.objects.get(id=step_data['mysql_info_id'])
            item['mysql_info'] = {
                "host": mysql_info_obj.host,
                "port": mysql_info_obj.port,
                "user": mysql_info_obj.user,
                "password": mysql_info_obj.password,
                "database": mysql_info_obj.table_name
            }
        else:
            item['mysql_info'] = {}

        step_list.append(item)
    one_data = {
        'steps_data': step_list,
        'url': environment_ip
    }
    # test_case_data['steps_data'] = step_list
    # test_case_data['url'] = environment_ip
    test_case_data.append(one_data)
    execution_test_case_data = {
        'remote_ip': remote_ip,  # 执行机ip
        'explicit_wait_timeout': explicit_wait_timeout,  # 显式等待超时时间
        'explicit_wait_poll_time': explicit_wait_poll_time,  # 显式等待轮询时间
        'implicitly_wait_timeout': implicitly_wait_timeout,  # 隐式等待时间
        'test_case_data': test_case_data
    }
    return execution_test_case_data


def get_one_test_scene_data(test_scene_id, environment_ip, remote_ip):
    """
    获取单个场景执行数据
    """
    explicit_wait_timeout = CommonParams.objects.get(id=1).param_value
    explicit_wait_poll_time = CommonParams.objects.get(id=2).param_value
    implicitly_wait_timeout = CommonParams.objects.get(id=3).param_value
    case_index_objs = UiSceneTestCaseIndex.objects.filter(scene_id=test_scene_id).order_by("test_case_index")

    for case_index_obj in case_index_objs:
        is_need_param = 0
        # 此用例是否具有参数
        test_case_id = case_index_obj.test_case_id
        if not TestCaseData.objects.filter(test_case_id=test_case_id):
            return error_response('场景{}下测试用例{}不存在测试步骤'.format(test_case_id, test_case_id))
        scene_param_objs = UiSceneParams.objects.filter(test_case_index_id=case_index_obj.id)
        # 查询场景下 用例 是否具有历史数据
        if not scene_param_objs:
            # 无历史数据的情况下 根据测试用例生成默认参数
            case_step_objs = TestCaseData.objects.filter(test_case_id=int(test_case_id)).order_by("sort")
            param_dic = {}
            for case_step_obj in case_step_objs:
                if case_step_obj.is_need_value:
                    is_need_param = 1
                    if case_step_obj.func_common_param_id:
                        common_obj = CommonParams.objects.get(id=case_step_obj.func_common_param_id)
                        value = common_obj.param_value
                    else:
                        value = case_step_obj.func_param
                elif case_step_obj.is_need_assert:
                    is_need_param = 1
                    value = case_step_obj.assert_value
                else:
                    continue
                param_dic[case_step_obj.step_desc] = value
            if param_dic:
                test_scene_data_obj = UiSceneParams(test_case_index_id=int(case_index_obj.id),
                                                    param_dic=str(param_dic), sort=1)
                test_scene_data_obj.save()
            case_index_obj.is_need_param = is_need_param
            case_index_obj.save()


    test_case_data = []
    scene_exe_time = len(UiSceneParams.objects.filter(test_case_index_id=case_index_objs[0].id))
    # 根据第一个用例的 参数条目 确认场景的执行次数
    for index in range(0, scene_exe_time):
        step_list = {"url": environment_ip, "steps_data": []}
        for case_index_obj in case_index_objs:
            case_index_id = case_index_obj.id
            scene_params_objs = UiSceneParams.objects.filter(test_case_index_id=case_index_id).order_by("sort")
            # if not case_index_obj.is_need_param:
            #     # 若此用例无参数 则跳过
            #     continue
            try:
                scene_params_obj = scene_params_objs[index]
                # 若此用例本条参数不存在 退出拼接
            except Exception as _:
                break
            param_dic = eval(scene_params_obj.param_dic)
            step_objs = TestCaseData.objects.filter(test_case_id=case_index_obj.test_case_id).order_by('sort')
            for step_obj in step_objs:
                item = {}
                step_desc = step_obj.step_desc
                if step_obj.is_need_assert:
                    try:
                        item['assert_value'] = param_dic[step_desc]
                    except Exception as _:
                        raise Exception("场景出现未配置参数 重新配置后执行")
                else:
                    item['assert_value'] = ''
                if step_obj.is_need_value:
                    try:
                        item['value'] = param_dic[step_desc]
                    except Exception as _:
                        raise Exception("场景出现未配置参数 重新配置后执行")
                else:
                    item['value'] = ''
                if step_obj.mysql_info_id:
                    mysql_info_obj = MysqlInfo.objects.get(id=step_obj.mysql_info_id)
                    item['mysql_info'] = {
                        "host": mysql_info_obj.host,
                        "port": mysql_info_obj.port,
                        "user": mysql_info_obj.user,
                        "password": mysql_info_obj.password,
                        "database": mysql_info_obj.table_name
                    }
                else:
                    item['mysql_info'] = {}
                item['step_desc'] = step_desc.split("_sort")[-2] if "_sort" in step_desc else step_desc
                item['ele_attribute'] = step_obj.ele_attribute
                item['function'] = step_obj.operate_func
                item['function_method'] = step_obj.action_func
                item['location'] = step_obj.location_func
                item['location_param'] = step_obj.location_value

                step_list["steps_data"].append(item)
        test_case_data.append(step_list)

    execution_test_case_data = {
        'remote_ip': remote_ip,  # 执行机ip
        'explicit_wait_timeout': explicit_wait_timeout,  # 显式等待超时时间
        'explicit_wait_poll_time': explicit_wait_poll_time,  # 显式等待轮询时间
        'implicitly_wait_timeout': implicitly_wait_timeout,  # 隐式等待时间
        'test_case_data': test_case_data
    }
    return execution_test_case_data


# 定时任务执行调用
def ui_one_thread(request_data):
    scene_id = request_data.get('scene_id')
    environment_id = request_data.get('environment_id')
    create_user = request_data.get('create_user')
    task_id = request_data.get('task_id')
    remote_ip = request_data.get('remote_ip')
    flag, data = get_one_test_scene_data(scene_id, environment_id, remote_ip)
    if not flag:
        TaskControl.objects.filter(id=task_id).update(job_status=4, execution_status=3)  # 修改为执行失败
        return False, '生成数据失败{}'.format(scene_id)
    script_execution = ui_script_execution()
    try:
        report_data = script_execution.execution_ui_scene_case(data)
    except Exception as e:
        TaskControl.objects.filter(id=task_id).update(job_status=4, execution_status=3)  # 修改为执行失败
        return False, '执行失败！！！'
    report_data['tester'] = create_user  # 添加测试人
    api_report_serializers = ApiTestReportSerializers(data=report_data)
    if api_report_serializers.is_valid():
        api_report_serializers.save()
    TaskControl.objects.filter(id=task_id).update(job_status=3, execution_status=3)  # 修改为执行成功
    scene_obj = UiTestScene.objects.get(id=scene_id)
    html_text = """
            尊敬的领导：
            <div style="text-indent:2em;">您好！</div>
            <div style="text-indent:2em;">您相关的测试场景：{},已执行完毕</div>
            <div style="text-indent:2em;"><strong>开始时间</strong>：{}    </div>
            <div style="text-indent:2em;"><strong>结束时间</strong>：{}    </div>
            <div style="text-indent:2em;"><strong>测试结果</strong>：{}    </div>
            <br>
            <div style="text-indent:4em;"><a href="{}">查看详细报告</a></div>
            <br><br><br><br>
    """.format(scene_obj.scene_name, report_data.get('start_time'), report_data.get('spend_time'), report_data.get('test_result'), report_data.get('report_src'))
    send_emails("测试报告", html_text, request_data.get('mails'))  # TODO  邮件后续发送

