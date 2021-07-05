import json
from django.views import View
from system_settings.taskjob.singleton import scheduler
from system_settings.taskjob.task_base_service import TaskBaseService
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


scheduler.start()
add_job = TaskBaseService()
add_job.add_jobs()

#创建
@csrf_exempt
@require_http_methods(["POST"])
def createTask( request):
        """
        创建任务
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            data = json.loads(request.body.decode("utf-8"))
            new_ticket_result, msg = TaskBaseService.new_task(data)
            return successResponse(data=new_ticket_result)
        except Exception as e:
            logger.error("新增定时任务异常：{}".format(str(e)))
        return errorResponse(str(e))

#启动任务
@csrf_exempt
@require_http_methods(["GET"])
def taskStart(request, *args, **kwargs):
        """
        启动任务
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:

            task_id = kwargs.get('task_id')
            start_task_result, msg = TaskBaseService.start_task(task_id)
            if start_task_result:
                return successResponse(data=start_task_result)
            else:
                return errorResponse(msg=msg)

        except Exception as e:
            logger.error("启动定时任务异常：{}".format(str(e)))
        return errorResponse(str(e))


#停止任务
@csrf_exempt
@require_http_methods(["GET"])
def taskStop(request, *args, **kwargs):
        """
        停止任务
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:

            task_id = kwargs.get('task_id')
            stop_task_result, msg = TaskBaseService.stop_task(task_id)
            if stop_task_result:
                return successResponse(data=stop_task_result)
            else :
                return  errorResponse(msg=msg)
        except Exception as e:
            logger.error("停止定时任务异常：{}".format(str(e)))
        return errorResponse(str(e))


#修改任务时间：包括暂停任务，再修改、再发布任务
@csrf_exempt
@require_http_methods(["GET"])
def taskUpdate(request, *args, **kwargs):
        """
        停止任务
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            task_id = kwargs.get('metter_id')
            stop_task_result, msg = TaskBaseService.stop_task(task_id)
            if stop_task_result:
                return successResponse(data=stop_task_result)
            else :
                return  errorResponse(msg=msg)
        except Exception as e:
            logger.error("停止定时任务异常：{}".format(str(e)))
        return errorResponse(str(e))




#任务列表
@csrf_exempt
@require_http_methods(["GET"])
def taskList(request, *args, **kwargs):
        """
        任务列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            job_result = TaskBaseService.get_job_list()
            return successResponse(data = { "list": job_result })
        except Exception as e:
            logger.error("任务列表异常：{}".format(str(e)))
        return errorResponse(str(e))




