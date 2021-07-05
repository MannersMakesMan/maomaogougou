import threading
from queue import Queue


def thead(task_queue, func):
    while not task_queue.empty():  # 若队列不为空继续运行
        task = task_queue.get()
        func(task)


def thread_task_main(task_ls, thread_num, func):
    """
    多线程任务模型
    :param task_ls:  任务列表
    :param thread_num:  线程数量
    :param func: 任务的执行函数
    :return:
    """
    task_queue = Queue()
    for task in task_ls:
        task_queue.put(task)

    # 创建2个线程
    poll = []  # 线程池
    for i in range(1, thread_num+1):
        thead_one = threading.Thread(target=thead, args=(task_queue, func, ))
        poll.append(thead_one)
    for n in poll:
        n.start()

    return


def print_func(a):
    print(a)


if __name__ == '__main__':

    thread_task_main([1, 2, 3, 4], 2, print_func)
