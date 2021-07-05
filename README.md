### 1.API文档 基于swagger  
链接：http://192.168.0.17:8000/doc/  

### 2.app结构  
####(1).account_system --> 账户管理  
####(2).asset_information --> 资产管理  
####(3).automated_testing --> 自动化测试数据管理  
####(4).basic_configuration --> 基础配置  
####(5).test_exe_conf --> 自动化测试执行管理(后续将会与automated_testing合并)  
####(6).automatic_api --> API自动化测试框架  
####(7).zy_api_testing --> API自动化测试后端  

### 3.后端部署(linux)  
pip install -r requirements.txt    
#####(1).开发  
python manage.py runserver 0.0.0.0:8000   
#####(2).生产  
###### 启动gunicorn  
gunicorn basic_configuration.wsgi -c gunicorn_conf.py    
###### 关闭gunicorn  
pstree -ap | grep gunicorn  
kill -9 12345  
###### 启动nginx  
nginx -c /usr/local/nginx/conf/nginx.conf  
###### 关闭nginx  
service nginx stop  


