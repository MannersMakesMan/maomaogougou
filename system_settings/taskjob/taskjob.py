# from home_application.pmo.tools import generatethrafivbstatistics
# from home_application.tarmanage.app_manage_views import delimage, FILE_LIST
# from home_application.pmo.views import selfsetremind_time, autoReminder, matterStatistics, syncUsersFromDing


def test(a, b, c):
    print('start_Task')


class TaskJob():
    def __init__(self):
        pass

    # 每次调用创建一个定时任务
    @classmethod
    def selfsetTimematter(self, a, b, c):
        test(a, b, c,)

    # 每次调用创建一个定时任务
    @classmethod
    def selfsetTimeTask(self, job_type, task_id):
        from zy_api_testing.tools import deal_time_task
        if job_type in [0, '0']:  # 执行api测试场景
            deal_time_task(task_id, job_type)
        elif job_type in [1, '1']:  # 执行ui测试场景   TODO 方法待添加
            deal_time_task(task_id, job_type)
