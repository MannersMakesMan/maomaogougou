from account_system.models import Department
import hashlib
from django.db.models import Q

def get_department(id):
    departments = Department.objects.filter(Q(superdepartment=id))
   # departments = Department.objects.filter(Q(tag=1))
    department_infos = [{'department_name': k.department_name, 'id': k.id} for k in departments]
    return department_infos

def get_root_department():
  #  departments = Department.objects.filter(Q(superdepartment_id=fid)&Q(tag =1))
   # department_infos=[]
    departments = Department.objects.get(tag="1")
    # for k in departments:
    #     department_infos.append(
    #         {
    #             'department_name':k.department_name,
    #             'id':k.id
    #         }
    #     )

      # lowerdepartment = Department.objects.filter(superdepartment=department_infos[0]['id'])

   # department_infos = [{'department_name': k.department_name, 'id': k.id} for k in departments]
    return departments

def get_group_by_user(user):
    groups = []
    usergroup = Department.objects.get(user=user)
    groups.append(usergroup.group.name)  # 得到这个用户的上一级组织架构，这里是直销一组

    def is_group(fid):
        if fid == 0:
            return True
        else:
            return False

    def get_groups(fid, groups):

        if is_group(fid):
            # group = GroupInfo.objects.get(id = fid)
            # groups.append(group.name)
            groups.reverse()
            group_infos = {}
            for k in range(len(groups)):
                group_infos['group_' + str(k + 1)] = groups[k]
            return group_infos // {'group_3': u'直销一组', 'group_2': u'政府..', 'group_1': u'一级组织'}
        else:
            group = Department.objects.get(id=fid)
            groups.append(group.name)  # groups=[u'直销一组',u'政府..',u'一级组织']
            return get_groups(group.fid, groups)

    return get_groups(usergroup.group.fid, groups)  # 调用内部函数get_group


def getPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

import random

def get_code():
    code_list = []
    for i in range(10):
        code_list.append(str(i))
    for i in range(10):
        code_list.append(str(i))
    for i in range(10):
        code_list.append(str(i))
    code = random.sample(code_list,5)   #随机取6位数
    code_num = ''.join(code)
    return  code_num


if __name__ == '__main__':
    str = "root15()"
    print(getPassword(str))
