# coding:utf-8
import json
import os

# def loadConfig():
# 	data = open("config.json")
# 	setting = json.load(data)
# 	data.close()
# 	return setting

class Config(object):
	SECRET_KEY = '4Z7naifZ8uPJnHHXQaR4LoUIlrI8eUA6MocxtLV5WrL3KqAFk177QIXbryYa2eySlX7sUuqrSH'


# json_config = loadConfig()
class LocalhostConfig(Config):
	basedir = os.path.abspath(os.path.dirname(__file__))
	DEBUG = True

	REDIS_HOST = '127.0.0.1'
	REDIS_PORT = 6379
	REDIS_DB = 4
	REDIS_PASSWORD = 'BCnb1jzIzHW9'

	# SQLITE_INFO = 'sqlite:///'+ os.path.join(basedir,'fashion.sqlite')
	SQLITE_INFO = "mysql://root:penny5921929@127.0.0.1:3306/fashion?charset=utf8"
	SERVER_URL = "http://localhost:5000/"

	SQLALCHEMY_DATABASE_URI = SQLITE_INFO
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_COMMIT_ON_TEARDOWN =True

	YunPian_APIKEY = "sDysNShY76MiSZhJmp3rtsFfOZabNrPo" # 云片网短信接口API Key

	MAIL_SERVER = "smtp.mxhichina.com"  # 邮件服务器地址
	MAIL_PORT = 465			   # 邮件服务器端口
	MAIL_USE_SSL = True
	MAIL_USE_TLS = False		  # 启用 TLS
	MAIL_USERNAME = "ceshi@163.com"
	MAIL_PASSWORD = "maKjRcJwz7Z5"

Conf = LocalhostConfig