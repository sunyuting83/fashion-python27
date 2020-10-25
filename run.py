# coding:utf-8
# from meinheld import patch
# patch.patch_all()
# from meinheld import server
# from meinheld import middleware
from flask import Flask

from uploader import Uploader
from config import Conf

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


from manage import api as manage_blueprint
app.register_blueprint(manage_blueprint, url_prefix='/manage')

from mobile import api as mobile_blueprint
app.register_blueprint(mobile_blueprint, url_prefix='/mobile')


if __name__ == '__main__':

	@app.route('/')
	def hello_world():
		return 'Hello World!'

	app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
	# server.listen(("0.0.0.0", 5000))
	# server.run(middleware.ContinuationMiddleware(app))
