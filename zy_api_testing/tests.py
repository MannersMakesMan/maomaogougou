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
    for key, value in params_data.items():
      if isinstance(value, str) or (isinstance(value, list) and len(value) == 0):  # 无下级数据的结构
        node_data[key] = ''
      elif isinstance(value, dict):  # 下级结构数据为 对象
        self.deal_object(key, node_data, value)
      elif isinstance(value, list):  # 下级结构数据为 数组
        node_data[key] = [{}]
        self.deal_array(node_data[key][0], value)

  def deal_object(self, key, node_data, params_data):
    for now_key, value in params_data.items():
      if isinstance(value, str) or (isinstance(value, list) and len(value) == 0):  # 无下级数据的结构
        node_data[key + '.' + now_key] = ''
      elif isinstance(value, dict):  # 下级结构数据为 对象
        self.deal_object(key + '.' + now_key, node_data, value)
      elif isinstance(value, list):  # 下级结构数据为 数组
        # if not node_data.get(key):
        #     node_data[key] = {}
        node_data[key + '.' + now_key] = [{}]
        self.deal_array(node_data[key + '.' + now_key][0], value)

  def deal_array(self, node_data, params_data):
    for now_key, value in params_data[0].items():
      if isinstance(value, str) or (isinstance(value, list) and len(value) == 0):  # 无下级数据的结构
        node_data[now_key] = ''
      elif isinstance(value, dict):  # 下级结构数据为 对象
        self.deal_object(now_key, node_data, value)
      elif isinstance(value, list):  # 下级结构数据为 数组
        node_data[now_key] = [{}]
        self.deal_array(node_data[now_key][0], value)

  def get_data(self):
    return self.build_json


if __name__ == "__main__":
    json = {
        "code": [{
              "name":"string",
              "code":{"da":[]}
            }],
        "data": {
            "connSql": [{
              "name":"string",
              "code":'sds'
            }],
            "createTime":  [{
              "name":"string",
              "code":'sds'
            }],
            "createUserId": [],
            "createUserName": "string",
            "destTable": "string",
            "enableFlag": "string",
            "filterSql": "string",
            "id": 0,
            "infoCode": "string",
            "infoName": "string",
            "infoProvideCode": "string",
            "infoProvideName": "string",
            "nextStrategy": "string",
            "rowsScript": 0,
            "sqlType": "string",
            "srcMainTable": "string",
            "strategyCode": "string",
            "strategyName": "string",
            "ukey": "string",
            "update": '',
            "updateTime": "string",
            "updateUserId": "string",
            "updateUserName": "string"
        },
        "msg": "string",
        "winRspType": "SUCC"
    }
    dada = MakeDataParamStructure(json)
    data = dada.get_data()
    print(data)
    deal = DealRequestJsonPartData(data)
    deal_data = deal.get_data()
    print(deal_data)

    # 查询总行   api/  response_ls
{'code': {'value': None, 'type': 'string', 'description': '返回状态码(根据不同状态码处理不同业务结果)', 'example': '', 'format': ''}, 'data': {'value': [{'address': {'value': None, 'type': 'string', 'description': '地址', 'example': '', 'format': ''}, 'advanceDrawFlag': {'value': None, 'type': 'string', 'description': '提前支取标志：0-否、1-是', 'example': '', 'format': ''}, 'advanceDrawFlagName': {'value': None, 'type': 'string', 'description': '提前支取标志名称：0-否、1-是', 'example': '', 'format': ''}, 'agentQualificationFlag': {'value': None, 'type': 'string', 'description': '代销资质标识', 'example': '', 'format': ''}, 'agentQualificationFlagName': {'value': None, 'type': 'string', 'description': '代销资质标识名称', 'example': '', 'format': ''}, 'auditStatus': {'value': None, 'type': 'string', 'description': '审核状态', 'example': '', 'format': ''}, 'auditStatusName': {'value': None, 'type': 'string', 'description': '审核状态-名称', 'example': '', 'format': ''}, 'auditTime': {'value': None, 'type': 'string', 'description': '审核时间', 'example': '', 'format': ''}, 'auditUserId': {'value': None, 'type': 'string', 'description': '审核人', 'example': '', 'format': ''}, 'bankCode': {'value': None, 'type': 'string', 'description': '总行编码：对应机构的机构代码', 'example': '', 'format': ''}, 'bankName': {'value': None, 'type': 'string', 'description': '银行名称', 'example': '', 'format': ''}, 'blackListFlag': {'value': None, 'type': 'string', 'description': '黑名单：0-否、1-是', 'example': '', 'format': ''}, 'blackListFlagName': {'value': None, 'type': 'string', 'description': '黑名单名称：0-否、1-是', 'example': '', 'format': ''}, 'city': {'value': None, 'type': 'string', 'description': '地址-市编码', 'example': '', 'format': ''}, 'commonGrade': {'value': None, 'type': 'string', 'description': '常用等级', 'example': '', 'format': ''}, 'commonGradeName': {'value': None, 'type': 'string', 'description': '常用等级名称', 'example': '', 'format': ''}, 'companyEmail': {'value': None, 'type': 'string', 'description': '邮箱', 'example': '', 'format': ''}, 'createTime': {'value': None, 'type': 'string', 'description': '创建时间', 'example': '', 'format': ''}, 'createUserId': {'value': None, 'type': 'string', 'description': '创建用户ID', 'example': '', 'format': ''}, 'createUserName': {'value': None, 'type': 'string', 'description': '创建用户名', 'example': '', 'format': ''}, 'creditRating': {'value': None, 'type': 'string', 'description': '最新评级', 'example': '', 'format': ''}, 'creditRatingName': {'value': None, 'type': 'string', 'description': '最新评级名称', 'example': '', 'format': ''}, 'id': {'value': None, 'type': 'integer', 'description': '主键ID', 'example': '', 'format': 'int64'}, 'linkMan': {'value': None, 'type': 'string', 'description': '联系人', 'example': '', 'format': ''}, 'linkMode': {'value': None, 'type': 'string', 'description': '联系方式', 'example': '', 'format': ''}, 'listFlag': {'value': None, 'type': 'string', 'description': '上市标识', 'example': '', 'format': ''}, 'listFlagName': {'value': None, 'type': 'string', 'description': '上市标识名称', 'example': '', 'format': ''}, 'listScale': {'value': None, 'type': 'string', 'description': '上市规格（亿元）', 'example': '', 'format': ''}, 'province': {'value': None, 'type': 'string', 'description': '地址-省编码', 'example': '', 'format': ''}, 'qualification': {'value': None, 'type': 'string', 'description': '机构资质', 'example': '', 'format': ''}, 'remark': {'value': None, 'type': 'string', 'description': '备注', 'example': '', 'format': ''}, 'rivalGrade': {'value': None, 'type': 'string', 'description': '对手方评级：数据字典', 'example': '', 'format': ''}, 'rivalGradeName': {'value': None, 'type': 'string', 'description': '对手方评级名称：数据字典', 'example': '', 'format': ''}, 'shortNameCn': {'value': None, 'type': 'string', 'description': '银行简称', 'example': '', 'format': ''}, 'subBankCode': {'value': None, 'type': 'string', 'description': '支行编码：对应机构的机构代码（分行或支行）', 'example': '', 'format': ''}, 'subBankName': {'value': None, 'type': 'string', 'description': '支行名称', 'example': '', 'format': ''}, 'trusteeshipQualificationFlag': {'value': None, 'type': 'string', 'description': '托管资质标识', 'example': '', 'format': ''}, 'trusteeshipQualificationFlagName': {'value': None, 'type': 'string', 'description': '托管资质标识名称', 'example': '', 'format': ''}, 'updateTime': {'value': None, 'type': 'string', 'description': '更新时间', 'example': '', 'format': ''}, 'updateUserId': {'value': None, 'type': 'string', 'description': '更新用户ID', 'example': '', 'format': ''}, 'updateUserName': {'value': None, 'type': 'string', 'description': '更新用户名', 'example': '', 'format': ''}, 'whiteListFlag': {'value': None, 'type': 'string', 'description': '白名单：0-否、1-是', 'example': '', 'format': ''}, 'whiteListFlagName': {'value': None, 'type': 'string', 'description': '白名单名称：0-否、1-是', 'example': '', 'format': ''}}], 'type': 'array', 'description': '', 'example': '', 'format': ''}, 'msg': {'value': None, 'type': 'string', 'description': '返回信息', 'example': '', 'format': ''}, 'winRspType': {'value': None, 'type': 'string', 'description': '返回类型', 'example': '', 'format': ''}}

