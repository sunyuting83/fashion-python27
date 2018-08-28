# fashion-python27 服装批发应用后端

一套使用Flask + sqlalchemy + redis + mysql 开发的服装批发APP应用后端

# 环境准备

1、安装Redis

2、安装MySQL

3、安装Python 2.7 并创建虚拟环境

4、pip install -r requirements.txt

5、进入Mysql建立新库，并导入fashion.sql


# 修改配置文件

修改config.py

  SECRET_KEY
  
  MYSQL_INFO 修改Mysql连接用户名、密码、数据库
  
  YunPian_APIKEY 云片短信api key
  
  Redis 和 Mail 相关设置
  

# 可能发生的报错：

MySQLdb ImportError: libmysqlclient.so.18

解决办法：


32位系统：

ln -s /usr/local/mysql/lib/libmysqlclient.so.18 /usr/lib/libmysqlclient.so.18

64位系统：

ln -s /usr/local/mysql/lib/libmysqlclient.so.18 /usr/lib64/libmysqlclient.so.18


# 运行：

python run.py

# 后台管理地址：

http://yourip/manage/

admin: 用户名：admin1   密码：123456789

组长: 用户名：ceshi1   密码：123456789

组员: 用户名：zuyuan1  密码：123456789


# mobile目录是供前台请求的api
