# 列表页多条件查询抽取 ，暂时只支持等值查询 ， 不支持模糊查询
import copy
import json
import re

from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import model_to_dict

from automatic_api.api_scene_execution import api_scene_execution
from automatic_ui.ui_script_execution import ui_script_execution
from basic_configuration.settings import EMAIL_HOST_USER
from common.thread_task import thread_task_main
from common.tools import send_emails
from system_settings.models import Dataexplain, DataDictionary, TaskControl
from test_exe_conf.models import ApiTestReport
from test_exe_conf.serializers import ApiTestReportSerializers, UiTestReportSerializers
from user_interface_test.models import UiTestScene
from user_interface_test.tools import get_one_test_scene_data
from zy_api_testing.models import SceneApiConf, ApiParams, ApiManage, Scene, SingleApiParams
from time import *


def api_list_query(data, page, page_size, model, sort_field, query_params, has_parent=False, accurate_ls=[]):
    """
    :param data: request.GET
    :param page: 页数
    :param page_size: 每页元素个数
    :param query_params: 列表  包含 所有可能查询的元素键， 需与数据库字段名对应上
    :param has_parent: True：精准查询， False ：模糊查询
    :param accurate_ls: 指定只能精准查找的字段列表，优先于has_parent字段的模糊查询
    :model : 数据库模型类
    :sort_field : 排序field , ex   'id' /  '-id'


    模糊查询优先级  ：
        1. has_parent 为True时，为所有字段精准查询 ，此时accurate_ls 无需传值
        2. has_parent 为False时，为所有不在accurate_ls内的字段模糊查询， accurate_ls内的字段精准查找
    :return:
    """
    need_contains = True if has_parent else False
    where = Q()
    for i in range(len(query_params)):
        key = query_params[i]
        if need_contains == False:
            has_parent = True if key in accurate_ls else False
        query_params[i] = data.get(query_params[i])
        if query_params[i]:
            tempStr = " where & Q(" + key + "='" + query_params[
                i] + "')" if has_parent else " where & Q(" + key + "__contains='" + query_params[i] + "')"
            where = eval(tempStr)
    queryset = model.objects.filter(where).order_by(sort_field)
    total = len(queryset)
    paginator = Paginator(queryset, page_size)  # paginator对象
    try:
        obm = paginator.page(page)
    except:
        obm = []
    return total, obm


class DelException(Exception):
    pass


# 解析请求参数为前端所需格式
class DealRequestConf(object):

    def __init__(self, params, deal_type=None, params_position=None):
        # try:
        self.params = params
        self.deal_type = deal_type
        self.params_position = params_position
        self.end_list = []  # 最终返回解析后数据
        self.deter_type(self.params, self.end_list)
        self.deal_anaytype()
        # except Exception as e:
        #     print(params)

    def deter_type(self, data, end_list):
        if isinstance(data, dict):
            self.dict_del(data, end_list, False)
        elif isinstance(data, list):
            self.array_del(data, end_list, is_children=False)

    def array_del(self, data, end_list, is_children=False):
        # 解析所有数组/列表数据
        for i in data:
            self.dict_del(i, end_list, is_children)

    def dict_del(self, data, end_list, is_children):
        # 解析所有字段/对象数据
        for key, value in data.items():
            item = {}
            if self.deal_type == 'assert':
                item['assert_type'] = ''
            item['param'] = key
            item['type'] = value.get('type')
            item['description'] = value.get('description')
            key_list = list(data.keys())
            item['id'] = key_list.index(key)
            item['is_ignore_key'] = 1 if value.get('is_ignore_key') else 0
            item['is_children'] = 1 if is_children else 0
            if self.params_position:
                item['param_in'] = self.params_position
            if isinstance(value, dict) and value.get('type') == 'array':
                value_type = value.get('value') if value.get('value') else value.get('items')
                if value_type:
                    # if value_type and value_type[0] == {'type': 'string'}:
                    if value_type and isinstance(value_type[0].get('type'), str):
                        # 数组下无层级数据， 如 list = [1,2,3], 无需递归
                        pass
                    else:
                        # 数组下包含层级关系， 包含字典 or 数组
                        # item['children'] = []
                        # item['children'].append([])
                        # self.array_del(value.get('value'),  item['children'][0])
                        item['children'] = []
                        # item['children'].append([])
                        self.array_del(value.get('value'), item['children'], is_children=True)
            # else:
            #     print(value.get('type'))

            end_list.append(item)

    def deal_anaytype(self):
        for i in self.end_list:
            if self.deal_type == 'assert':
                i['param'] = 'rep.' + i['param']

    def get_data(self):
        return self.end_list


class Resolver(object):
    def __init__(self, params, params_in=None):
        self.param_in = params_in
        # self.params = eval(params)
        self.params = copy.deepcopy(params)
        self.end_dict = {}
        self.deter_type(self.params, self.end_dict)

    def deter_type(self, params, vessel):
        # 判断类型 ， 分发到不同解析场景
        if isinstance(params, list):
            self.deal_array(params, vessel)
        elif isinstance(params, dict):
            self.deal_dict(params, vessel)

    def deal_array(self, params, vessel):
        # 解析数组形式数据
        for i in params:
            if isinstance(i, dict):
                self.deal_dict(i, vessel)

    def deal_dict(self, params, vessel):
        # 解析字段类型数据
        key = params.get('param')
        param_in = params.get('param_in')
        if key and param_in == self.param_in:
            # if re.match('\.', key):
            self.deal_key(params, key)

    def deal_key(self, params, name_str):
        # 处理字段名层级问题
        key_list = name_str.split('.')

        list_length = len(key_list)
        now_node = self.end_dict  # 当前层级
        for i in key_list:
            if i in now_node.keys():  # 当前 层级存在
                now_node = now_node[i]
            else:
                if key_list.index(i) + 1 == list_length:  # 为最后一层时
                    now_node[i] = ''
                    self.set_in_params(now_node, i, params)
                else:
                    now_node[i] = {}
                    now_node = now_node[i]  # 传递层级标记

    def set_in_params(self, now_node, i, params):
        if params.get('type') == 'array' and params.get('children'):  # 列表包含字典数据开启下层
            now_node_list_data = []

            k_list = [[]]
            # base_param_list = []
            max_index = 0
            # 1 . 获取出基本参数key
            # 2. 计算出列表下字典参数最大下标
            # 2. 根据基本参数key 拼接每个dict下参数为一个列表 为k
            for one_param in params.get('children'):
                has_index = re.search('\[([0-9]{1,3})\]', one_param.get('param'))
                if not has_index:
                    # base_param_list.append(one_param.get('param'))  # 添加基础字段
                    k_list[0].append(one_param)
                else:
                    max_index = int(has_index.group(1)) if max_index < int(has_index.group(1)) else max_index
            if max_index != 0:
                for index in range(2, max_index + 1):
                    k_list.append([])
                    for this_param in params.get('children'):
                        now_index = re.search('\[{}\]'.format(index), this_param.get('param'))
                        if now_index:
                            this_param['param'] = this_param.get('param').replace('[{}]'.format(index), '')
                            k_list[index - 1].append(this_param)
            for k in k_list:
                next_obj = Resolver(k, self.param_in)
                now_node_list_data.append(next_obj.get_end_dict())
            now_node[i] = now_node_list_data
        elif params.get('type') == 'array':
            now_node[i] = str(params.get('value').split(',')) if params.get('value') else []
            if (params.get('is_ignore_key')):
                self.end_dict = list(now_node.values())[0]
                print(self.end_dict)
        else:  # 非列表数据直接存储到最终结构
            if isinstance(params.get('value'), str):
                value = params.get('value').split('.')
                if len(value) > 1 and params.get('value').startswith('before_rep'):
                    end_value = value[0]
                    for key in range(1, len(value)):
                        if re.search('(\[[0-9]{1,9}\])', value[key]):  # ex: data[8] 匹配获取列表数据
                            data_list = value[key].split('[')
                            end_value += "['{}']{}".format(data_list[0], "[" + data_list[1])
                        else:
                            end_value += "['{}']".format(value[key])
                    now_node[i] = end_value
                else:
                    # now_node[i] = params.get('value')
                    now_node[i] = type_chenge(params.get('type'), params.get('value'))
            else:
                # now_node[i] = params.get('value')
                now_node[i] = type_chenge(params.get('type'), params.get('value'))

    def get_end_dict(self):
        return self.end_dict


def type_chenge(type, value):
    try:
        if type in ['integer', 'number']:
            value = int(value)
        elif type == 'string':
            value = str(value)
        elif type == 'boolean':
            value == bool(value)
    except Exception as e:
        pass
    return value


class AssertDataDealResolver(object):

    def __init__(self, params):
        self.end_list = []
        self.params = copy.deepcopy(params)
        # self.deal_data(self.params)
        self.start_deal(self.params)

    def start_deal(self, params_list):
        for param_dict in params_list:
            if param_dict.get('type') == 'array' and param_dict.get('children'):
                # 处理树形数据
                base_param = self.deal_data(param_dict)
                self.deal_children_param(base_param, param_dict['children'])
            else:  # 无下级数据直接添加
                self.deal_data(param_dict)
                if param_dict.get('type') == 'array':
                    param_dict['value'] = param_dict.get('value').split(',')
                self.end_list.append(param_dict)

    def deal_children_param(self, base_param, children_list):
        for children_dict in children_list:
            deal_param = self.deal_children_dict_param(children_dict)
            children_dict['param'] = base_param + deal_param

            if children_dict.get('type') == 'array' and children_dict.get('children'):
                self.deal_children_param(children_dict['param'], children_dict['children'])
            else:
                if children_dict.get('type') == 'array':
                    children_dict['value'] = children_dict.get('value').split(',')
                self.end_list.append(children_dict)

    def deal_data(self, param):
        # self.end_list = self.params
        # for param in params:
        end_value = ''
        if re.search('\.', param.get('param')):  # 仅当参数中存在.时需要转化
            param_key = param.get('param').split('.')
            end_value = param_key[0]
            for key in range(1, len(param_key)):
                if re.search('(\[[0-9]{1,9}\])', param_key[key]):  # ex: data[8] 匹配获取列表数据
                    data_list = param_key[key].split('[')
                    end_value += "['{}']{}".format(data_list[0], "[" + data_list[1])
                else:
                    end_value += "['{}']".format(param_key[key])
            param['param'] = end_value
            # param['value'] = type_chenge(param.get('type'), param.get('value'))
        return end_value if end_value else param['param']
        # self.end_list.append(param)
        # self.end_list[self.end_list.index(param)]['param'] = end_value

    def deal_children_dict_param(self, children_dict):
        end_value = ''
        # if re.search('\.', children_dict.get('param')):  # 仅当参数中存在.时需要转化
        index = int(re.search('\[([0-9]{1,3})\]', children_dict.get('param')).group(1)) if re.search('\[([0-9]{1,3})\]',
                                                                                                     children_dict.get(
                                                                                                         'param')) else 0
        param_key = children_dict.get('param').replace('[{}]'.format(index), '').split(
            '.') if index != 0 else children_dict.get('param').split('.')
        end_value = '[' + str(index) + ']' + "['" + param_key[0] + "']" if index == 0 else '[' + str(
            index - 1) + ']' + "['" + param_key[0] + "']"
        for key in range(1, len(param_key)):
            # re_group = re.search('(\[[0-9]{1,9}\])', param_key[key])
            # if re_group:  # ex: data[8] 匹配获取列表数据
            #     data_list = param_key[key].split('[')
            #     end_value += "['{}']{}".format(data_list[0], "[" + data_list[1])
            # else:
            end_value += "['{}']".format(param_key[key])
        children_dict['param'] = end_value
        # children_dict['value'] = type_chenge(children_dict.get('type'), children_dict.get('value'))
        return end_value if end_value else children_dict['param']

    def get_end_list(self):
        return self.end_list


def juged_type(params):
    if not isinstance(params, list):
        params = eval(params)
    for i in params:
        if i.get('type') == "before_rep":
            return False
        if i.get('type') == 'array' and i.get('children'):  # 列表包含字典数据开启下层
            for k in i.get('children'):
                flag = juged_type(k)
                if not flag:
                    return False
    return True


# 校验场景第一个接口，入参配置 type 字段是否存在 before_res
def check_one_request_conf(request_conf):
    for conf in request_conf:
        if conf.get('type') == 'before_rep':
            return False
        if conf.get('type') == 'array' and conf.get('children'):
            # for children in conf.get('children'):
            #     flag = check_one_request_conf(children)
            flag = check_one_request_conf(conf.get('children'))  # 修改了下级参数的结构
            if not flag:
                return False
    return True


def need_login_scene(scene, environment_ip):
    # 拼接的登录接口参数 参数到场景请求参数中
    api_data = []
    try:
        item = {}
        data_id = Dataexplain.objects.get(dictionary_code='A0000001').id  # 获取登录配置id
        login_api_path = DataDictionary.objects.get(Dataexplain_id=data_id,
                                                    DictionarySubitem_code='a0000001').dictionary_item1  # 获取登录接口路径
        send_token_key = DataDictionary.objects.get(Dataexplain_id=data_id,
                                                    DictionarySubitem_code='a0000002').dictionary_item1  # 发送token的key位置
        get_token_key = DataDictionary.objects.get(Dataexplain_id=data_id,
                                                   DictionarySubitem_code='a0000003').dictionary_item1  # 获取token的key位置
        user_key = DataDictionary.objects.get(Dataexplain_id=data_id,
                                              DictionarySubitem_code='a0000004').dictionary_item1  # 获取用户名的key
        user_value = DataDictionary.objects.get(Dataexplain_id=data_id,
                                                DictionarySubitem_code='a0000004').dictionary_item2  # 获取用户名的值
        password_key = DataDictionary.objects.get(Dataexplain_id=data_id,
                                                  DictionarySubitem_code='a0000005').dictionary_item1  # 获取密码的key
        password_value = DataDictionary.objects.get(Dataexplain_id=data_id,
                                                    DictionarySubitem_code='a0000005').dictionary_item2  # 获取密码的值

        try:
            api_obj = ApiManage.objects.get(path=login_api_path)  # 接口源数据
        except:
            return False, '登录接口配置错误，未收录登录接口！！！'
        param_in = eval(api_obj.param_in)
        if len(param_in) == 1:
            body = {}
            body[user_key] = user_value
            body[password_key] = password_value

            request_params = {
                param_in[0]: body
            }
        else:
            body = {}
            body[user_key] = user_value
            body[password_key] = password_value

            request_params = {
                'body': body
            }
        request_params['headers'] = {}
        item['request_params'] = request_params
        item['assert_data'] = []  # 断言  请求头传空字
        item['global_param_key'] = send_token_key  # 后续请求键名
        item['global_param_value'] = get_token_key  # 获取键名
        item['api_desc'] = api_obj.api_desc
        item['request_method'] = api_obj.request_method
        item['path'] = environment_ip + '/' + api_obj.server + api_obj.path
        api_data.append(item)
        scene.append(api_data)
        return True, scene
    except Exception as e:
        return False, '登录接口配置错误，请查看配置！！！'


# 获取执行单个场景api请求数据
def deal_scene(scene_id, environment_ip):
    """
    :param scene_id: 场景id
    :return: request_list
    """
    scene = []

    # 判断是否为需要登录的场景 -- 是 则添加到第一个接口参数
    if not Scene.objects.filter(id=scene_id):
        return False, "场景不存在"
    if Scene.objects.get(id=scene_id).need_login == 1:
        # 需要登录的场景 ，拼接登录接口为第一个接口的请求参数
        flag, msg = need_login_scene(scene, environment_ip)
        if not flag:
            return False, msg
    # 根据排序值查询 场景下接口
    if SceneApiConf.objects.filter(scene=scene_id):
        one_api_data_list = list(SceneApiConf.objects.filter(scene=scene_id).order_by('sort').values('id', 'api'))
        for api_data in one_api_data_list:
            # 获取单个接口的所有次数 执行请求数据
            a_api = []
            scene_id = api_data.get("id")
            api_manage_obj = model_to_dict(ApiManage.objects.filter(id=api_data.get('api')).first())
            api_params_objs = ApiParams.objects.filter(api_conf_id=scene_id).order_by('sort')


            for api_param in api_params_objs:
                one_api_request_params = {}  # 单个接口的单次请求参数
                data = model_to_dict(api_param)
                request_params = eval(data.get('end_request_json').replace('null,', 'None,').replace('null}', 'None}'))
                assert_data = eval(data.get('end_asset_json').replace('null,', 'None,').replace('null}', 'None}'))
                request_params['headers'] = {   # TODO 49专用
                    'Authorization': 'dev'
                }
                one_api_request_params['request_params'] = request_params
                one_api_request_params['assert_data'] = assert_data
                # one_api_request_params['global_param_key'] = '20222'
                # one_api_request_params['global_param_value'] = '11111'
                one_api_request_params['api_desc'] = api_manage_obj.get('api_desc')
                one_api_request_params['request_method'] = api_manage_obj.get('request_method')
                if api_manage_obj.get('server') == 'default':
                    one_api_request_params['path'] = environment_ip + api_manage_obj.get('path')
                else:
                    one_api_request_params['path'] = environment_ip + '/' + api_manage_obj.get('server') + api_manage_obj.get('path')
                a_api.append(one_api_request_params)  # 添加单次请求数据
            scene.append(a_api)  # 添加单接口多次请求数据
        return True, scene
    else:
        return False, '场景id错误'


# 获取执行单个场景api请求数据
def deal_single_api(single_api_id, environment_ip, need_login):
    """
    :param scene_id:
    :return: request_list
    """
    single_api_data = []

    # 判断是否为需要登录的场景 -- 是 则添加到第一个接口参数
    api_manage_objs = ApiManage.objects.filter(id=single_api_id)
    if not api_manage_objs:
        return False, "此api不存在"
    single_api_param_objs = SingleApiParams.objects.filter(api_id=single_api_id).order_by('sort')
    if not single_api_param_objs:
        return False, "此api无测试数据"
    if need_login:
        # 需要登录的场景 ，拼接登录接口为第一个接口的请求参数
        flag, msg = need_login_scene(single_api_data, environment_ip)
        if not flag:
            return False, msg
    # 根据排序值查询 场景下接口
    a_api = []
    for api_param in single_api_param_objs:
        one_api_request_params = {}  # 单个接口的单次请求参数
        data = model_to_dict(api_param)
        request_params = eval(data.get('end_request_json').replace('null,', 'None,').replace('null}', 'None}'))
        assert_data = eval(data.get('end_asset_json').replace('null,', 'None,').replace('null}', 'None}'))
        # request_params['headers'] = {   # TODO 49专用
        #     'Authorization': 'dev'
        # }
        one_api_request_params['request_params'] = request_params
        one_api_request_params['assert_data'] = assert_data
        # one_api_request_params['global_param_key'] = '20222'
        # one_api_request_params['global_param_value'] = '11111'
        one_api_request_params['api_desc'] = api_manage_objs[0].api_desc
        one_api_request_params['request_method'] = api_manage_objs[0].request_method
        if api_manage_objs[0].server == 'default':
            one_api_request_params['path'] = environment_ip + api_manage_objs[0].path
        else:
            one_api_request_params['path'] = environment_ip + '/' + api_manage_objs[0].server + api_manage_objs[0].path
        a_api.append(one_api_request_params)  # 添加单次请求数据
    single_api_data.append(a_api)  # 添加单接口多次请求数据
    return True, single_api_data



from django.utils import timezone as Dtimezone


# api定时任务触发方法
def deal_time_task(task_id, task_type):
    """
    params:
        task_id : 定时任务id
    """
    # 从定时任务中获取环境id , 场景id
    task = TaskControl.objects.filter(id=task_id)
    if not task:
        return False, '不存在的任务'
    # 修改任务状态 ,记录开始时间
    start_time = time()
    start_time_task = Dtimezone.now().strftime("%Y-%m-%d %H:%M:%S")
    TaskControl.objects.filter(id=task_id).update(job_status=2)  # 修改为执行中
    test_config = eval(task.first().test_config)
    environment_path = task.first().environment.Test_address  # 测试环境地址
    mails = task.first().mails.split(';') if task.first().mails else []  # TODO  后续发送邮件
    create_user = task.first().create_user  # TODO  后续发送邮件
    request_data_list = []
    for scene_id in test_config:
        request_data = {
            'environment_id': environment_path,
            'mails': mails,
            'create_user': create_user,
            'scene_id': scene_id,
            'task_id': task_id,
            'task_type': task_type,
        }
        if task_type in [1, "1"]:
            # UI自动化测试
            request_data['remote_ip'] = task.first().performMachine.perform_ip
        request_data_list.append(request_data)
    # thread_task_main(request_data_list, 1, one_thread)  # 执行批量
    # email_str = """             尊敬的领导：
    #             <div style="text-indent:2em;">您好！</div>"""
    email_str = """
    <html>
 <head></head>
 <body>
  <center>
   <strong><font size="5px" color="red">UI自动化测试任务</font></strong>
  </center>
  <table align="center" border="5">
   <tbody>
    <tr>
    <th>场景名称</th>
    <th>开始时间</th>
    <th>花费时间</th>
    <th>测试结果</th>
    <th>测试报告</th>
  </tr>
    """
    end_str = """
       </tbody>
          </table>
         </body>
        </html>
    """
    for i in request_data_list:
        email_body = one_thread(i)
        email_str = email_str+email_body

    send_emails("测试报告", email_str+end_str, i.get('mails'))  # TODO  邮件后续发送

    end_time = time()
    end_time_task = Dtimezone.now().strftime("%Y-%m-%d %H:%M:%S")
    expend_time = start_time - end_time
    TaskControl.objects.filter(id=task_id).update(expend_time=expend_time, start_time=start_time_task,
                                                  end_time=end_time_task)  # 修改为执行中
    # 修改任务状态, 记录结束时间


def one_thread(request_data):
    scene_id = request_data.get('scene_id')
    environment_id = request_data.get('environment_id')
    create_user = request_data.get('create_user')
    task_id = request_data.get('task_id')
    task_type = request_data.get('task_type')
    if task_type in ["0", 0]:
        flag, data = deal_scene(scene_id, environment_id)
        if not flag:
            TaskControl.objects.filter(id=task_id).update(job_status=4, execution_status=3)  # 修改为执行失败
            return False, '生成数据失败{}'.format(scene_id)
        try:
            scene_execution = api_scene_execution()
            report_data = scene_execution.scene_execution(data)
        except Exception as e:
            TaskControl.objects.filter(id=task_id).update(job_status=4, execution_status=3)  # 修改为执行失败
            return False, '执行失败！！！'
        report_data['tester'] = create_user  # 添加测试人
        report_data['test_type'] = 'API-场景测试(定时任务)-{}'.format(Scene.objects.get(id=scene_id).scene_name)
        api_report_serializers = ApiTestReportSerializers(data=report_data)
        if api_report_serializers.is_valid():
            api_report_serializers.save()
        TaskControl.objects.filter(id=task_id).update(job_status=3, execution_status=3)  # 修改为执行成功
        scene_obj = Scene.objects.get(id=scene_id)

    elif task_type in ["1", 1]:
        try:
            remote_ip = request_data.get('remote_ip')
            execution_test_case_data = get_one_test_scene_data(scene_id, environment_id, remote_ip)
            script_execution = ui_script_execution()
            report_data = script_execution.execution_ui_scene_case(execution_test_case_data)
        except Exception as e:
            TaskControl.objects.filter(id=task_id).update(job_status=4, execution_status=3, execute_log=e.args[0])  # 修改为执行失败
            return False, '执行失败！！！'

        report_data['tester'] = create_user  # 添加测试人
        report_data['test_type'] = 'UI-场景测试(定时任务)-{}'.format(UiTestScene.objects.get(id=scene_id).scene_name)
        ui_report_serializers = UiTestReportSerializers(data=report_data)
        if ui_report_serializers.is_valid():
            ui_report_serializers.save()
        TaskControl.objects.filter(id=task_id).update(job_status=3, execution_status=3)  # 修改为执行成功
        scene_obj = UiTestScene.objects.get(id=scene_id)
    # html_text = """
    #         <div style="text-indent:2em;">您相关的测试场景：{},已执行完毕</div>
    #         <div style="text-indent:2em;"><strong>开始时间</strong>：{}    </div>
    #         <div style="text-indent:2em;"><strong>花费时间</strong>：{}    </div>
    #         <div style="text-indent:2em;"><strong>测试结果</strong>：{}    </div>
    #         <br>
    #         <div style="text-indent:4em;"><a href="{}">查看详细报告</a></div>
    #         <br>
    # """.format(scene_obj.scene_name, report_data.get('action_time'), report_data.get('spend_time'),
    #            report_data.get('result'), report_data.get('report_src'))
    html_text = """
    <tr>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td><a href="{}">查看详细报告</a></td>
  </tr>
    """.format(scene_obj.scene_name, report_data.get('action_time'), report_data.get('spend_time'),report_data.get('result'), report_data.get('report_src'))
    return html_text










# 拼接api_params 多行为表格数据
def deal_api_params(api_params_objs):
    end_putin_list = []
    end_assert_list = []
    try:
        if len(api_params_objs) > 0:
            gen_putin_data = eval(api_params_objs[0].get('putin_params_json').replace('null,', 'None,').replace('null}', 'None}'))  # 取第一个为源数据  后续添加 value + index
            gen_assert_data = eval(
                api_params_objs[0].get('asset_json').replace('null,', 'None,').replace('null}', 'None}'))
            end_putin_list = gen_putin_data
            end_assert_list = gen_assert_data
        for params_index in range(1, len(api_params_objs)):
            putin_json = eval(
                api_params_objs[params_index].get('putin_params_json').replace('null,', 'None,').replace('null}',
                                                                                                         'None}'))
            assert_json = eval(
                api_params_objs[params_index].get('asset_json').replace('null,', 'None,').replace('null}', 'None}'))
            for i in range(len(putin_json)):
                putin_value_key = 'value' + str(params_index)
                gen_putin_data[i][putin_value_key] = putin_json[i].get('value')
            for k in range(len(assert_json)):
                assert_value_key = 'value' + str(params_index)
                gen_assert_data[k][assert_value_key] = assert_json[k].get('value')

            end_putin_list = gen_putin_data
            end_assert_list = gen_assert_data
        return end_putin_list, end_assert_list
    except Exception as e:
        print(111)



class DealRequestJsonPartData():
    """
  处理部分 请求json 单位置（如： body， headers） 参数

  ep ： 字典型参数 用.连接, 数组型参数 ， type=‘arraty’  下级参数以列表形式存放在 value中
  """

    def __init__(self, params_data):
        self.end_data = {}
        self.params_data = params_data
        self.dispatcher(self.end_data, self.params_data)

    # 根据不同类型进行分发
    def dispatcher(self, node_data, params_data):
        if isinstance(params_data, dict):
            self.deal_object(node_data, params_data)
        elif isinstance(params_data, list):
            self.deal_array(node_data, params_data)

    # 处理字典型数据
    def deal_object(self, node_data, params_data):
        for key, value in params_data.items():
            if isinstance(value, list):
                node_data[key] = {
                    'value': [],
                    'type': 'array',
                    'description': '',
                    'example': '',
                    'format': ''
                }
                self.deal_array(node_data[key], value)
            else:
                node_data[key] = {
                    'value': '',
                    'type': '',
                    'description': '',
                    'example': '',
                    'format': ''
                }
                if isinstance(value, str) and value == 'int':
                    node_data[key]['type'] = 'integer'
                elif isinstance(value, str) and (value == 'true' or value == 'false'):
                    node_data[key]['type'] = 'boolean'
                else:
                    node_data[key]['type'] = 'string'

    # 处理数组型数据
    def deal_array(self, node_data, params_data):
        if len(params_data) == 0:  # 单数组 时
            node_data['value'] = [{
                'type': 'string',
                'format': 'None',
                'description': 'None'
            }]
        else:  # 数组下包含对象时
            node_data['value'] = [{}]
            self.deal_object(node_data['value'][0], params_data[0])

    def get_data(self):
        return self.end_data


class MakeDataParamStructure():
    """
      将对象结构参数所有下级参数 拼接到同一级
      ep: data.aaa
  """

    def __init__(self, start_json):
        self.build_json = {}
        self.start_json = start_json
        self.dispatcher(self.build_json, self.start_json)

    def dispatcher(self, node_data, params_data):
        # if isinstance(params_data, list):
        #     for key, value in params_data[0][0].items():
        #         if isinstance(value, str):  # 无下级数据的结构
        #             node_data[key] = ''
        #         elif (isinstance(value, list) and len(value) == 0) or (isinstance(value, list) and (
        #                 not isinstance(value[0], list) and not isinstance(value[0], dict))):
        #             node_data[key] = []
        #         elif isinstance(value, dict):  # 下级结构数据为 对象
        #             self.deal_object(key, node_data, value)
        #         elif isinstance(value, list):  # 下级结构数据为 数组
        #             node_data[key] = [{}]
        #             self.deal_array(node_data[key][0], value)
        # else:
        for key, value in params_data.items():
            if isinstance(value, str):  # 无下级数据的结构
                node_data[key] = ''
            elif (isinstance(value, list) and len(value) == 0) or (isinstance(value, list) and (not isinstance(value[0], list) and not isinstance(value[0], dict))):
                node_data[key] = []
            elif isinstance(value, dict):  # 下级结构数据为 对象
                self.deal_object(key, node_data, value)
            elif isinstance(value, list):  # 下级结构数据为 数组
                node_data[key] = [{}]
                self.deal_array(node_data[key][0], value)

    def deal_object(self, key, node_data, params_data):
        for now_key, value in params_data.items():
            if isinstance(value, str):  # 无下级数据的结构
                node_data[key + '.' + now_key] = ''
            elif (isinstance(value, list) and len(value) == 0) or (isinstance(value, list) and (not isinstance(value[0], list) and not isinstance(value[0], dict))):
                node_data[key + '.' + now_key] = []
            elif isinstance(value, dict):  # 下级结构数据为 对象
                self.deal_object(key + '.' + now_key, node_data, value)
            elif isinstance(value, list):  # 下级结构数据为 数组
                # if not node_data.get(key):
                #     node_data[key] = {}
                node_data[key+'.'+now_key] = [{}]
                self.deal_array(node_data[key+'.'+now_key][0], value)

    def deal_array(self, node_data, params_data):
        for now_key, value in params_data[0].items():
            if isinstance(value, str):  # 无下级数据的结构
                node_data[now_key] = ''
            elif (isinstance(value, list) and len(value) == 0) or (isinstance(value, list) and (not isinstance(value[0], list) and not isinstance(value[0], dict))):
                node_data[now_key] = []
            elif isinstance(value, dict):  # 下级结构数据为 对象
                self.deal_object(now_key, node_data, value)
            elif isinstance(value, list):  # 下级结构数据为 数组
                node_data[now_key] = [{}]
                self.deal_array(node_data[now_key][0], value)

    def get_data(self):
        return self.build_json


def deal_param_ls(param_ls, result):
    def add_param_data(result, path_param_data, param_in, name):
        result['name_ls'].append({"name": name})
        result['description_ls'].append(path_param_data['description'])
        result['type_ls'].append(path_param_data['type'])
        result['is_ignore_key_ls'].append(path_param_data.get("is_ignore_key_ls", None))
        result['param_in_ls'].append(param_in)
        return result

    def deal_body_param(body_param_ls, result):
        if "type" in body_param_ls:
            add_param_data(result, body_param_ls, "body", 'default')
        else:
            for index, name in enumerate(body_param_ls):
                body_param_data = body_param_ls[name]
                result = add_param_data(result, body_param_data, "body", name)
                if body_param_data.get("value", None):
                    result["name_ls"][index]["children"] = {"name_ls": [], "description_ls": [], "type_ls": [], "is_ignore_key_ls": [], "param_in_ls": []}
                    if body_param_data['type'] == "array":
                        deal_body_param(body_param_data["value"][0], result["name_ls"][index]["children"])
                    elif body_param_data['type'] == "object":
                        deal_body_param(body_param_data["value"], result["name_ls"][index]["children"])
                    else:
                        print(111)
                else:
                    pass
        return result

    if "path" in param_ls:
        # 参数在path
        path_param_ls = param_ls["path"]
        for name in path_param_ls:
            path_param_data = path_param_ls[name]
            result = add_param_data(result, path_param_data, 'path', name)

    elif "query" in param_ls:
        # 参数在query中
        path_param_ls = param_ls["query"]
        for name in path_param_ls:
            path_param_data = path_param_ls[name]
            result = add_param_data(result, path_param_data, 'query', name)

    else:
        # 参数在body中
        if "body" in param_ls:
            body_param_ls = param_ls["body"]
            result = deal_body_param(body_param_ls, result)
        else:
            result = deal_body_param(param_ls, result)
    return result




# 解析请求参数为前端所需格式
class DealRequestLsConf(object):

    def __init__(self, params, deal_type=None, params_position=None):
        # try:
        self.params = params
        self.deal_type = deal_type
        self.params_position = params_position
        self.end_list = []  # 最终返回解析后数据
        self.deter_type(self.params, self.end_list)
        self.deal_anaytype()
        # except Exception as e:
        #     print(params)

    def deter_type(self, data, end_list):
        if isinstance(data, dict):
            self.dict_del(data, end_list, False)
        elif isinstance(data, list):
            self.array_del(data, end_list, is_children=False)

    def array_del(self, data, end_list, is_children=False):
        # 解析所有数组/列表数据
        for i in data:
            self.dict_del(i, end_list, is_children)

    def dict_del(self, data, end_list, is_children):
        # 解析所有字段/对象数据
        for key, value in data.items():
            item = {}
            if self.deal_type == 'assert':
                item['assert_type'] = ''
            item['param'] = key
            item['type'] = value.get('type')
            item['description'] = value.get('description')
            key_list = list(data.keys())
            item['id'] = key_list.index(key)
            item['is_ignore_key'] = 1 if value.get('is_ignore_key') else 0
            item['is_children'] = 1 if is_children else 0
            if is_children:
                item['isopend_self'] = 0
            item['children'] = []
            if self.params_position:
                item['param_in'] = self.params_position
            if isinstance(value, dict) and value.get('type') == 'array':
                value_type = value.get('value') if value.get('value') else value.get('items')
                if value_type:
                    # if value_type and value_type[0] == {'type': 'string'}:
                    if value_type and isinstance(value_type[0].get('type'), str):
                        # 数组下无层级数据， 如 list = [1,2,3], 无需递归
                        pass
                    else:
                        # 数组下包含层级关系， 包含字典 or 数组
                        # item['children'] = []
                        # item['children'].append([])
                        # self.array_del(value.get('value'),  item['children'][0])
                        item['children'] = []
                        # item['children'].append([])
                        item['children_index']=2
                        self.array_del(value.get('value'), item['children'], is_children=True)
            # else:
            #     print(value.get('type'))

            end_list.append(item)

    def deal_anaytype(self):
        for i in self.end_list:
            if self.deal_type == 'assert':
                i['param'] = 'rep.' + i['param']

    def get_data(self):
        return self.end_list

class PutSameLayer():
    """
    转换json 存在上下级关系放在第一级， 用字段 parent_name 关联 代表上级参数名
    """
    def __init__(self, params_data):
        self.param_data = params_data
        self.find_next(self.param_data)

    def find_next(self, param_list):
        for param_dict in param_list:
            if len(param_dict.get('children')) > 0 and not param_dict.get('is_to_bottom'):   # 当前层存在下级  , 取出放到元数组中
                # 在元数组中找到当前元素所在下标
                now_index = param_list.index(param_dict)
                parent_name = param_dict.get('param')
                self.insert_next(parent_name, now_index, param_dict.get('children'))

    def insert_next(self, parent_name, start_index, children_list):
        now_index = start_index
        current_index = 0
        for children_dict in children_list:
            now_index = now_index + 1
            if len(children_dict.get('children')) > 0:
                children_dict['parent_name'] = parent_name
                children_dict['is_to_bottom'] = 1
                self.param_data.insert(now_index, children_dict)
                son_parent_name = children_dict.get('param')
                current_index = self.insert_next(son_parent_name, now_index, children_dict.get('children'))
            else:
                if current_index != 0:
                    current_index = current_index+1
                    now_index = current_index
                children_dict['parent_name'] = parent_name
                self.param_data.insert(now_index, children_dict)

        return now_index

    def get_data(self):
        return self.param_data


class DealToParamsJson():
    """
    解析成第二步参数  还原所有 上下级数据关系  --- 去除存在下级的占位列表 ，在元数组中寻找并插入到下级
    1 . 找不是子集  且有子集的数据， 递归查询所有子集数据是否有子集 ，无--归原层级中， 有--继续递归
    """
    def __init__(self, table_one_row_list):
        self.param_list = table_one_row_list
        self.need_remove_ls = []
        self.start_deal(self.param_list)

    def start_deal(self, param_list):
        for param_dict in param_list:
            if not param_dict.get('is_children') and len(param_dict.get('children')) > 0:
                param_dict['children'] = []  #  清空占位数据，用于装载真实子集数据
                self.find_son(param_dict.get('param'), param_dict['children'])
        self.remove_some()

    def find_son(self, parent_name, parent_children_list):
        for param_dict in self.param_list:
            if param_dict.get('parent_name') == parent_name and len(param_dict.get('children')) > 0:
                #  子集存在子集数据， 先将子集装载完毕
                param_dict['children'] = []  # 清空占位数据，用于装载真实子集数据
                self.find_son(param_dict.get('param'), param_dict['children'])
                parent_children_list.append(param_dict)
                self.need_remove_ls.append(param_dict)
            elif param_dict.get('parent_name') == parent_name:
                parent_children_list.append(param_dict)
                self.need_remove_ls.append(param_dict)

    def remove_some(self):
        for i in self.need_remove_ls:
            self.param_list.remove(i)

    def get_data(self):
        return self.param_list




# 递归判断参数是否存在历史值
def check_has_history_data(putin_params_conf, params_json):
    for in_conf in putin_params_conf:
        for params_data in params_json:
            if in_conf['param'] == params_data['param'] and not in_conf.get('children'):
                in_conf['value'] = params_data.get('value') if params_data.get('value') else ''
            elif in_conf['type'] == 'array' and in_conf.get('children') and params_data.get('children') and in_conf['param'] == params_data['param'] and params_data['type'] == 'array':
                check_has_history_data(in_conf['children'], params_data['children'])  # 开始递归

# 递归判断断言参数是否存在历史值
def check_has_assert_history_data(asset_conf, asset_json):
    for in_assert in asset_conf:
        for assert_data in asset_json:
            if in_assert['param'] == assert_data['param'] and not in_assert.get('children'):
                in_assert['value'] = assert_data.get('value') if assert_data.get('value') else ''
            elif in_assert['type'] == 'array' and in_assert.get('children') and assert_data.get('children') and in_assert['param'] == assert_data['param'] and assert_data['type'] == 'array':
                check_has_assert_history_data(in_assert['children'], assert_data['children'])  # 开始递归
