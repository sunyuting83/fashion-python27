# coding:utf-8
import json

# def loadConfig():
# 	data = open("config.json")
# 	setting = json.load(data)
# 	data.close()
# 	return setting

class Config(object):
	SECRET_KEY = 's9oV39FEtQ4A2cHN3AU2dRFDpegaEVgLzZOYKbdATD0oeHcPOmRgKzphIoBRVQSI'


# json_config = loadConfig()
class LocalhostConfig(Config):
	DEBUG = True

	REDIS_HOST = '127.0.0.1'
	REDIS_PORT = 6379
	REDIS_DB = 4
	REDIS_PASSWORD = '3SuLc0VvzLJm'

	MYSQL_INFO = "mysql://root:penny5921929@127.0.0.1:3306/fashion?charset=utf8"
	SERVER_URL = "http://localhost:5000/"

	SQLALCHEMY_DATABASE_URI = MYSQL_INFO
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_COMMIT_ON_TEARDOWN =True

	YunPian_APIKEY = "akfkxr6e9f5r4wqle4borkwwpoejmdyu" # 云片网短信接口API Key

	MAIL_SERVER = "smtp.mxhichina.com"  # 邮件服务器地址
	MAIL_PORT = 465			   # 邮件服务器端口
	MAIL_USE_SSL = True
	MAIL_USE_TLS = False		  # 启用 TLS
	MAIL_USERNAME = "ceshi@163.com"
	MAIL_PASSWORD = "d39LE5arbMFn"

Conf = LocalhostConfig