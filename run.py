# coding:utf-8
import os
import re
import json

from flask import Flask, request, render_template, url_for, make_response

from uploader import Uploader
from config import Conf
from model import db_session
import redis
from flask_cors import CORS

# def create_app():
app = Flask(__name__)
CORS(app, resources=r'/*') #跨域设置
app.config.from_object(Conf)
app.secret_key = app.config['SECRET_KEY']

app.redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'],
					db=app.config['REDIS_DB'], password=app.config['REDIS_PASSWORD'])

app.debug = app.config['DEBUG']

from test import api as test_blueprint
app.register_blueprint(test_blueprint, url_prefix='/test')

from manage import api as manage_blueprint
app.register_blueprint(manage_blueprint, url_prefix='/manage')

from mobile import api as mobile_blueprint
app.register_blueprint(mobile_blueprint, url_prefix='/mobile')

# from Manage import api as Manage_blueprint
# app.register_blueprint(Manage_blueprint, url_prefix='/Manage')


	# return app

#app = create_app()


if __name__ == '__main__':
	# app = create_app()

	@app.route('/')
	def hello_world():
		return 'Hello World!'

	app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, ssl_context=('/etc/ssl/168tv.co.crt','/etc/ssl/168tv.co.key'))
	# app.run(debug=True)
	# application.run(host='0.0.0.0')
