# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
# from home_application.pmo.models import TaskCrontabtask as Crontabtask
# from home_application.pmo.models import Job as Job
# from home_application.taskjob.taskjob import TaskJob
# from home_application.taskjob.singleton import scheduler
from system_settings.serializers import TaskSerializerQuery
from system_settings.taskjob.singleton import scheduler
from system_settings.taskjob.taskjob import TaskJob
from system_settings.models import TaskControl as Crontabtask

class TaskBaseService():
    """
    任务基础服务
    """

    def __init__(self):
        pass

    @classmethod
    def get_task_by_id(self, task_id):
        """
        获取任务对象
        :param ticket_id:
        :return:
        """
        task_obj = Crontabtask.objects.filter(id=task_id).first()
        if task_obj:
            return task_obj, ''
        else:
            return False, 'task is not existed'

    @classmethod
    def get_task_list(self, title='', username='', create_start='', create_end='', reverse=1, per_page=10, page=1):
        """
        任务列表
        :param title:
        :param username:
        :param create_start: 创建时间起
        :param create_end: 创建时间止
        :param state_ids: 状态id,str,逗号隔开
        :param reverse: 按照创建时间倒序
        :param per_page:
        :param page:

        :return:
        """
        query_params = Q()

        if title:
            query_params &= Q(title__contains=title)
        if create_start:
            query_params &= Q(gmt_created__gte=create_start)
        if create_end:
            query_params &= Q(gmt_created__lte=create_end)

        if reverse:
            order_by_str = '-create_time'
        else:
            order_by_str = 'create_time'

        query_params &= Q(creator=username)
        task_objects = Crontabtask.objects.filter(query_params).order_by(order_by_str)

        paginator = Paginator(task_objects, per_page)

        try:
            task_result_paginator = paginator.page(page)
        except PageNotAnInteger:
            task_result_paginator = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            task_result_paginator = paginator.page(paginator.num_pages)

        task_result_object_list = task_result_paginator.object_list
        task_result_restful_list = []

        #暂时无用

        # for task_result_object in task_result_object_list:
        #     # job_obj = Job
        #     creator_obj, msg = AccountBaseService.get_user_by_username(task_result_object.creator)
        #     if creator_obj:
        #         creator_info = dict(username=creator_obj.username, alias=creator_obj.alias,
        #                             is_active=creator_obj.is_active, email=creator_obj.email, phone=creator_obj.phone)
        #     else:
        #         creator_info = dict(username=creator_obj.username, alias='', is_active=False, email='', phone='')
        #
        #     task_result_restful_list.append(dict(id=task_result_object.id,
        #                                          task=task_result_object.name,
        #                                          job_name=task_result_object.job_id,
        #                                          cron_expression=task_result_object.cron_expression,
        #                                          state=task_result_object.state,
        #                                          creator=task_result_object.creator,
        #                                          creator_info=creator_info,
        #                                          last_modify_user=task_result_object.last_modify_user,
        #                                          last_modify_time=str(task_result_object.last_modify_time)[:19],
        #                                          create_time=str(task_result_object.create_time)[:19],
        #                                          ))
        return task_result_restful_list, dict(per_page=per_page, page=page, total=paginator.count)

    @classmethod
    def get_job_list(self, aQ, page, page_size):
        """
        查询作业列表
        :return:
        """
        queryset = Crontabtask.objects.filter(aQ).order_by("-id")

        total = len(queryset)  # 总数量
        paginator = Paginator(queryset, page_size)  # paginator对象
        try:
            obm = paginator.page(page)
            task_serialize = TaskSerializerQuery(obm, many=True)
            return_data = task_serialize.data

        except Exception as _e:
            return_data = []
        return {
                "data": return_data,
                "page": page,
                "total": total
        }


    @classmethod
    def new_task(self, request_data_dict):
        """
        新建任务
        :param request_data_dict:
        :param app_name:调用源app_name
        :return:
        """
        task_name = request_data_dict.get('task_name')
        des = request_data_dict.get('des', '')
        job_id = request_data_dict.get('job_id')
        cron_expression = request_data_dict.get('cron_expression')
        username = request_data_dict.get('username')
        email = request_data_dict.get('email')
        emp_no = request_data_dict.get('emp_no')
        url = request_data_dict.get('url')
        metter_id = request_data_dict.get('metter_id')
        state = request_data_dict.get('state')
        create_time = request_data_dict.get('create_time')

        new_task_obj = Crontabtask(name=task_name, des=des, job_id=job_id, cron_expression = cron_expression,
                                   creator = username,email = email,emp_no = emp_no,url = url, metter_id = metter_id,state=state,create_time=create_time )

        new_task_obj.save()
        return new_task_obj.id, ''

    @classmethod
    def start_task(self, task_id):
        """
        启动任务
        :param request_data_dict:
        :param app_name:调用源app_name
        :return:
        """
        task_obj, msg = self.get_task_by_id(task_id)
        if not task_obj:
            return False, msg

        task_name = task_obj.job_name
        task_des = task_obj.remark
        cron_expression = task_obj.end_cron_expression
        method = task_obj.method
        cron_list = []
        if cron_expression:
            cron_list = cron_expression.split('|')
            trigger = cron_list[0]

        para_dict = {}
        for item in cron_list:
            content = item.split('=')
            if len(content) > 1:
                para_dict[content[0]] = content[1]

        if not task_des:
            task_des = task_name

        if trigger == '0':
            jobs = scheduler.get_jobs()
            for i in jobs:
                if i.id == str(task_id):
                    return False, '该任务已存在'
            # '表达式错误，请填写正确表达式。如：0|2019-07-22 08:00:00 ，表示2019年7月22日8点0分0秒执行一次任务'
            task = scheduler.add_job(getattr(TaskJob, method), 'date', run_date=cron_list[1], id=str(task_id),
                                     args=[task_obj.job_type, task_id])
        elif trigger == '1':
            # '表达式错误，请填写正确表达式。如：1|*|3|10|10|10|*|*，周 天 小时 分 秒 开始时间 结束时间，表示每隔3天10小时10分钟10秒执行一次任务'
            task = scheduler.add_job(getattr(TaskJob, method), 'interval',
                                     weeks=int(para_dict.get('weeks') or 0), days=int(para_dict.get('days') or 0),
                                     hours=int(para_dict.get('hours') or 0), minutes=int(para_dict.get('minutes') or 0),
                                     seconds=int(para_dict.get('seconds') or 0), start_date=para_dict.get('start_date'),
                                     end_date=para_dict.get('end_date'), id=str(task_id),
                                     args=[task_obj.job_type, task_obj.id])
        elif trigger == '2':
            # '表达式错误，请填写正确表达式。如：2|*|6-8,11-12|3rd fri|*|*|*|*|*|*|* , 年 月 日 周 星期 小时 分 秒 开始时间 结束时间，
            # 表示每隔3天10小时10分钟10秒执行一次任务'
            task = scheduler.add_job(getattr(TaskJob, method), 'cron',
                                     year=para_dict.get('year'), month=para_dict.get('month'), day=para_dict.get('day'),
                                     week=para_dict.get('week'), day_of_week=para_dict.get('day_of_week'),
                                     hour=para_dict.get('hour'), minute=para_dict.get('minutes'),
                                     second=para_dict.get('second'), start_date=para_dict.get('start_date'),
                                     end_date=para_dict.get('end_date'), id=str(task_id),
                                     args=[task_obj.job_type, task_obj.id])

        print(scheduler.get_jobs())
        if task.id:
            task_obj.state = 1
            task_obj.job_status = 1
            task_obj.execution_status = 1
            task_obj.save()
            return task.name, ''
        else:
            return task.name, msg

    @classmethod
    def stop_task(self, task_id):
        task_obj = self.get_task_by_id(task_id)
        result = scheduler.remove_job(str(task_id))
        task_obj[0].state = 2
        task_obj[0].execution_status = 2
        # task_obj[0].job_status = 2
        task_obj[0].save()

        # jobs = scheduler.get_jobs()
        # for i in jobs:
        #     if i.id == str(task_id):
        #         result = scheduler.remove_job(str(i.id))
        #         if task_obj and not result:
        #             task_obj[0].state = 2
        #             task_obj[0].execution_status = 2
        #             # task_obj[0].job_status = 2
        #             task_obj[0].save()
        #             return True, ''
        #         else:
        #             return False, result
        # return False, '该任务不存在'
        return True, ''

    #根据id 更新
    @classmethod
    def update_task_by_id(self, id, request_data_dict):

        task_obj = Crontabtask.objects.filter(id=id).first()
        task_id = task_obj.id
        result = self.update_task(task_id,request_data_dict)

        return result

    #根据ID更新
    @classmethod
    def update_task(self, task_id):

        task_obj = self.get_task_by_id(task_id)
        result = scheduler.remove_job(str(task_id))

        # task_name = request_data_dict.get('task_name')
        # des = request_data_dict.get('des', '')
        # job_id = request_data_dict.get('job_id')
        # cron_expression = request_data_dict.get('cron_expression')
        # username = request_data_dict.get('username')
        # email = request_data_dict.get('email')
        # emp_no = request_data_dict.get('emp_no')
        # url = request_data_dict.get('url')

        if task_obj and not result:
            # task_obj[0].task_name =task_name
            # task_obj[0].des =des
            # task_obj[0].job_id =job_id
            # task_obj[0].cron_expression =cron_expression
            # task_obj[0].username =username
            # task_obj[0].email =email
            # task_obj[0].emp_no =emp_no
            # task_obj[0].url = url
            task_obj[0].state = 2
            task_obj[0].save()
            self.start_task(task_id)
            return True, ''
        else:
            return False, result

    @classmethod
    def add_jobs(self):
        task_objs = Crontabtask.objects.filter(state=1, execute_type__in=[1, 2, 3, '1', '2', '3'])
        for task in task_objs:
            self.start_task(task.id)
