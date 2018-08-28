# coding:utf-8
import requests
import json


class APITest(object):
	def __init__(self, base_url):
		self.base_url = base_url
		self.headers = {}

	def login(self, phone_number, password, path='/login'):
		payload = {'phone_number': phone_number, 'password': password}
		self.headers = {'content-type': 'application/json'}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		self.token = response_data.get('token')
		return response_data

	def user(self, path='/user'):
		self.headers = {'token': self.token}
		response = requests.get(url=self.base_url + path, headers=self.headers)
		response_data = json.loads(response.content)
		return response_data

	def logout(self, path='/logout'):
		self.headers = {'token': self.token}
		response = requests.get(url=self.base_url + path, headers=self.headers)
		response_data = json.loads(response.content)
		return response_data


	def register_step_1(self, phone_number, path='/register-step-1'):
		payload = {'phone_number': phone_number}
		self.headers = {'content-type': 'application/json'}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		print response_data.get('code')
		return response_data

	def register_step_2(self, phone_number, validate_number, path='/register-step-2'):
		payload = {'phone_number': phone_number, 'validate_number': validate_number}
		self.headers = {'content-type': 'application/json'}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		print response_data.get('code')
		return response_data

	def register_step_3(self, phone_number, password, password_confirm, path='/register-step-3'):
		payload = {'phone_number': phone_number, 'password': password, 'password_confirm': password_confirm}
		self.headers = {'content-type': 'application/json'}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		print response_data.get('code')
		return response_data

	def register_step_4(self, phone_number, mail, company, truename, path='/register-step-4'):
		payload = {'phone_number': phone_number, 'mail':mail, 'company':company, 'truename': truename}
		self.headers = {'content-type': 'application/json'}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		print response_data.get('code')
		return response_data

	# 提交留言
	def post_guestbook(self, path='/post_book'):
		payload = {"getnav": '这就是条留言。'}
		self.headers = {'content-type': 'application/json','token': self.token}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		print response_data.get('code')
		return response_data

	# 订单提交
	def post_order(self, path='/post_order'):
		payload = {
			"addressid":2,
			"orderitems":[
				{
					"proid": 27,
					"pronumber":"122-1112-111",
					"color":"蓝色",
					"size": "S",
					"number":100,
					"prace":158,
					"total":15800
				},
				{
					"proid": 27,
					"pronumber":"122-1112-111",
					"color":"蓝色",
					"size": "M",
					"number":400,
					"prace":158,
					"total":63200
				},
				{
					"proid": 27,
					"pronumber":"122-1112-111",
					"color":"蓝色",
					"size": "L",
					"number":200,
					"prace":158,
					"total": 31600
				},
				{
					"proid": 27,
					"pronumber":"122-1112-112",
					"color":"浅蓝",
					"size": "S",
					"number":100,
					"prace":158,
					"total":15800
				},
				{
					"proid": 27,
					"pronumber":"122-1112-112",
					"color":"浅蓝",
					"size": "L",
					"number":200,
					"prace":158,
					"total":31600
				},
				{
					"proid": 31,
					"pronumber":"122-1115-111",
					"color":"青蓝色",
					"size": "S",
					"number":100,
					"prace":158,
					"total":15800
				},
				{
					"proid": 31,
					"pronumber":"122-1115-112",
					"color":"淡绿色",
					"size": "M",
					"number":100,
					"prace":158,
					"total":15800
				}
			]
		}
		self.headers = {'content-type': 'application/json','token': self.token}
		response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
		response_data = json.loads(response.content)
		print response_data.get('code')
		return response_data


if __name__ == '__main__':
	api = APITest('http://127.0.0.1:5001')
	api.login('13623521583', 'kanghong')
	api.logout()


# from client import APITest

# api = APITest('http://127.0.0.1:5000/mobile')

# 注册
# api.register_step_1('13623521580')


# api.register_step_2('13623521580','767383')

# api.register_step_3('13623521580','kanghong','kanghong')

# api.register_step_4('13623521580','zhangdamin@sohu.com','北京博维思通有限公司','张大民')

# 登录
# data = api.login('13623521583', 'kanghong')

# 查看用户
# data = api.user()
# print data

# 注销
# data = api.logout()
# print data

# 提交留言
# api.post_guestbook()

# 提交订单
# api.post_order()