import multiprocessing

bind = '192.168.0.190:8000'
#bind = '0.0.0.0:8000'
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 4
# 进程数 生产环境推荐为 核数*2+1
threads = 1024
# 参数适用与多线程工作模式

backlog = 2048
worker_class = "gthread"
# 启动模式 gevent最优 多进程+异步模式 sync, eventlet, gevent, tornado, gthread
worker_connections = 1000
timeout = 1024
# 超时
daemon = True
# 是否后台启动
debug = True
# 是否启动debug模式
reload = True
proc_name = 'automatic_test_gunicorn'
# 进程名称
# pidfile = './log/gunicorn.pid'
# errorlog = './log/gunicorn.log'
