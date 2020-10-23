# coding:utf-8
from sqlalchemy import create_engine, ForeignKey, BigInteger, Column, Integer, String, Text, DateTime,\
	and_, or_, SmallInteger, Float, DECIMAL, Numeric, desc, asc, Table, join, event, func, exc, select, extract
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session, aliased, mapper
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.pool import SingletonThreadPool
import datetime
import json
from html.parser import HTMLParser
import cgi
import re
from config import Conf

Domain = 'http://api.1showroomonline.com'
print(Conf.SQLITE_INFO)
engine = create_engine(Conf.SQLITE_INFO, connect_args={'check_same_thread':False}, poolclass=SingletonThreadPool)

Base = declarative_base()

db_session = scoped_session(sessionmaker(autocommit=False,
										 autoflush=False,
										 bind=engine))

Base.query = db_session.query_property()

# 解决MYSQL链接超时的问题
@event.listens_for(engine, "engine_connect")
def ping_connection(connection, branch):
	if branch:
		# "branch" refers to a sub-connection of a connection,
		# we don't want to bother pinging on these.
		return

	try:
		connection.scalar(select([1]))
	except exc.DBAPIError as err:
		if err.connection_invalidated:
			connection.scalar(select([1]))
		else:
			raise


# 产品洗涤关联表
pro_to_wash = Table('pro_to_wash',
	Base.metadata,
	Column('product_id', Integer, ForeignKey('fa_product.proid')),
	Column('wash_id', Integer, ForeignKey('fa_pro_wash.id'))
)

# 图片表
class Images(Base):
	__tablename__ = 'fa_images'

	id = Column('id', Integer, primary_key=True, index=True)
	picid = Column('picid', Integer, ForeignKey('fa_pro_color.id'))
	picurl = Column('picurl', String)
	sort = Column('sort', SmallInteger)

	def __repr__(self):
		return '<Images %r%r%r>' % (self.id, self.picid, self.picurl)

	# 图片处理函数
	@hybrid_property
	def colorpic_split(self):
		if not self.picurl:
			return []
		# return self.img_url.picurl.split(',')
		imgurl = self.picurl.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	# 后端单个色组图片处理
	@hybrid_property
	def thispic_split(self):
		if not self.picurl:
			return ''
		imgurl = self.picurl.split(',')
		return imgurl[2]

	# 得到图片数据
	def to_dict(self):
		return self.thispic_split


# 系统日志表
class ActionLog(Base):
	__tablename__ = 'fa_log'

	id = Column('id', Integer, primary_key=True, index=True)
	username = Column('username', String(30))
	actions = Column('actions' , String(100))
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())

	def __repr__(self):
		return '<ActionLog %r%r%r%r>' % (self.id, self.username, self.actions, self.addtime)


# 管理用户组表
class Group(Base):
	__tablename__ = 'fa_admin_group'

	group_id = Column('group_id', Integer, primary_key=True)
	name = Column('name', String(30), index=True)
	power = Column('power', SmallInteger)
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())
	manageid = relationship("Manage", uselist=False, back_populates="group")

	def __repr__(self):
		return '<Group %r%r>' % (self.name,self.power)

# 管理用户组表
class Team(Base):
	__tablename__ = 'fa_team'

	id = Column('id', Integer, primary_key=True, index=True)
	title = Column('title', String(80))
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())

	# 关联管理员所属组
	manageid = relationship("Manage", uselist=False, back_populates="team")

	# 关联客户所属组
	usersteam = relationship("Users", uselist=False, back_populates="team")

	def __repr__(self):
		return '<Team %r%r%r>' % (self.id, self.title, self.addtime)

# 管理用户表
class Manage(Base):
	__tablename__ = 'fa_manage'

	id = Column('id', Integer, primary_key=True)
	username = Column('username', String(11), index=True)
	password = Column('password', String(60))
	login = Column('login', Integer)
	last_login_ip = Column('last_login_ip', String(20))
	last_login_time = Column('last_login_time', DateTime)
	status = Column('status', String(60))
	purview = Column('purview',Integer)
	login_size = Column('login_size',Integer)
	title = Column('title', String(30))
	name = Column('name', String(30))
	phone = Column('phone', BigInteger)
	mail = Column('mail', String(100))
	wechat = Column('wechat', String(50))
	contact = Column('contact', SmallInteger)

	group_id = Column('group_id', Integer,ForeignKey('fa_admin_group.group_id'))
	group = relationship("Group", back_populates="manageid")

	teamid = Column('teamid',Integer ,ForeignKey('fa_team.id'))
	team = relationship("Team", back_populates="manageid")

	# 消息已读一的一方
	reads = relationship('MuGb', backref='fa_manage', lazy='dynamic')


	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	# 查询用户登录
	@classmethod
	def login_check(cls, user_name, user_password):
		user = db_session.query(Manage).filter(Manage.username == user_name, Manage.password == user_password, Manage.status == 0).first()
		# print(str(user))
		if not user:
			return None

		return user


	def __repr__(self):
		return '<Manage %r>' % (self.username)

	# 获取汉字首字母
	@hybrid_property
	def get_cn_first_letter(self,codec="UTF8"):
		if not self.name:
			return 'A'
		if codec!="GBK":
			if codec!="unicode":
				self.name=self.name.decode(codec)
			self.name=self.name.encode("GBK")

		if self.name<"\xb0\xa1" or self.name>"\xd7\xf9":
			return "X"
		if self.name<"\xb0\xc4":
			return "A"
		if self.name<"\xb2\xc0":
			return "B"
		if self.name<"\xb4\xed":
			return "C"
		if self.name<"\xb6\xe9":
			return "D"
		if self.name<"\xb7\xa1":
			return "E"
		if self.name<"\xb8\xc0":
			return "F"
		if self.name<"\xb9\xfd":
			return "G"
		if self.name<"\xbb\xf6":
			return "H"
		if self.name<"\xbf\xa5":
			return "J"
		if self.name<"\xc0\xab":
			return "K"
		if self.name<"\xc2\xe7":
			return "L"
		if self.name<"\xc4\xc2":
			return "M"
		if self.name<"\xc5\xb5":
			return "N"
		if self.name<"\xc5\xbd":
			return "O"
		if self.name<"\xc6\xd9":
			return "P"
		if self.name<"\xc8\xba":
			return "Q"
		if self.name<"\xc8\xf5":
			return "R"
		if self.name<"\xcb\xf9":
			return "S"
		if self.name<"\xcd\xd9":
			return "T"
		if self.name<"\xce\xf3":
			return "W"
		if self.name<"\xd1\x88":
			return "X"
		if self.name<"\xd4\xd0":
			return "Y"
		if self.name<"\xd7\xf9":
			return "Z"

	def to_dict(self):
		return {
			'title': self.title,
			'name': self.name,
			'phone': self.phone,
			'mail': self.mail,
			'wechat': self.wechat,
			'pingying': self.get_cn_first_letter
		}


# 分类表
class Classify(Base):
	__tablename__ = 'fa_class'

	classid = Column('classid', Integer, primary_key=True)
	topid = Column('topid',	Integer)
	classname = Column('classname', String(50), index=True)
	icon = Column('icon', Integer, ForeignKey(Images.id))
	ctype = Column('ctype',	SmallInteger)
	display = Column('display',	SmallInteger)
	sort = Column('sort',	SmallInteger)
	uptime = Column('uptime', DateTime,default=datetime.datetime.now())
	# 一对一关联分类图片
	icon_url = relationship('Images', backref=backref('fa_class'))

	@classmethod
	def classify_check(cls):
		classify = db_session.query(Classify).filter(Classify.ctype == 0, Classify.display == 0).order_by(Classify.sort)
		if not classify:
			return None

		return classify

	def __repr__(self):
		return '<Classify %r%r%r%r%r%r%r%r>' % (self.classid, self.topid, self.classname, self.icon, self.ctype, self.display, self.sort, self.uptime)

	# 图片处理函数
	@hybrid_property
	def icon_split(self):
		if not self.icon_url:
			return []
		imgurl = self.icon_url.picurl.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	def to_dict(self):
		return {
			'classid': self.classid,
			'topid': self.topid,
			'classname': self.classname,
			'icon': self.icon_split,
			'sort': self.sort
		}

# 产品颜色表
class ProColor(Base):
	__tablename__ = 'fa_pro_color'
	id = Column('id', Integer, primary_key=True, index=True)
	proid = Column('proid',	Integer, ForeignKey('fa_product.proid'))
	colortitle = Column('colortitle', String(20))
	color = Column('color', String(20))
	number = Column('number', String(20))
	cover = Column('cover', String)
	picurl = Column('picurl', String)
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())

	# 分类图片一的一方
	colorpic = relationship("Images", backref="fa_pro_color", lazy='dynamic')

	def __repr__(self):
		return '<ProColor %r%r%r%r%r%r%r%r>' % (
			ProColor.proid, 
			ProColor.colortitle, 
			ProColor.color,
			ProColor.number,
			ProColor.cover,
			ProColor.picurl,
			ProColor.addtime, 
			ProColor.colorpic
		)

# 产品洗涤说明表
class Wash(Base):
	__tablename__ = 'fa_pro_wash'

	id = Column('id', Integer, primary_key=True, index=True)
	icon = Column('icon',	Integer)
	text = Column('text', String)

	@classmethod
	def wash_check(cls):
		wash = db_session.query(Wash)
		if not wash:
			return None

		return wash

	def __repr__(self):
		return '<Wash %r%r%r>' % (Wash.id, Wash.icon, Wash.text)

# 产品洗涤说明表
class Size(Base):
	__tablename__ = 'fa_product_size'

	id = Column('id', Integer, primary_key=True, index=True)
	size_title = Column('size_title', String)
	size = Column('size', String)

	@classmethod
	def size_check(cls):
		size = db_session.query(Size)
		if not size:
			return None

		return size

	def __repr__(self):
		return '<Size %r%r%r>' % (Size.id, Size.size_title, Size.size)

# 产品推荐类型表
class Recommend(Base):
	__tablename__ = 'fa_recommend'

	id = Column('id', Integer, primary_key=True, index=True)
	topid = Column('topid',	Integer)
	icon = Column('icon',	Integer, ForeignKey(Images.id))
	titles = Column('titles', String)
	sort = Column('sort',	SmallInteger)
	# 一对一关联分类图片
	icon_url = relationship('Images', backref=backref('fa_recommend'))

	@classmethod
	def recommend_check(cls):
		recommend = Recommend.query
		if not recommend:
			return None

		return recommend

	def __repr__(self):
		return '<Recommend %r%r%r%r>' % (Recommend.id, Recommend.topid, Recommend.icon, Recommend.titles)

	# 图片处理函数
	@hybrid_property
	def icon_split(self):
		if not self.icon_url:
			return []
		imgurl = self.icon_url.picurl.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	def to_dict(self):
		return {
			'id': self.id,
			'topid': self.topid,
			'titles': self.titles,
			'icon': self.icon_split,
			'sort': self.sort
		}



# 产品表
class Product(Base):
	__tablename__ = 'fa_product'

	proid = Column('proid', Integer, primary_key=True, index=True)
	pid = Column('pid',	Integer, ForeignKey(Classify.classid))
	oldpid = Column('oldpid',	Integer)
	creatorid = Column('creatorid', Integer, ForeignKey(Manage.id))
	teamid = Column('teamid', Integer, ForeignKey(Team.id))
	proname = Column('proname', String(100))
	price = Column('price', String(20))
	text_centont = Column('text_centont', String(200))
	model_height = Column('model_height',	Integer)
	fabric = Column('fabric', String(60))
	lining = Column('lining', String(60))
	wash = Column('wash', String(30))
	size_table = Column('size_table', String)
	weights = Column('weights', String(30))
	the_net = Column('the_net', String(30))
	first_order = Column('first_order', String(100))
	again_order = Column('again_order', String(100))
	shipping = Column('shipping',	Integer)
	flying = Column('flying',	Integer)
	new_p = Column('new_p',	SmallInteger, ForeignKey(Recommend.id))
	covers = Column('covers', Integer, ForeignKey(Images.id))
	place = Column('place', String(20))
	colorid = Column('colorid',	String)
	size = Column('size', String)
	display = Column('display',	SmallInteger)
	add_time = Column('add_time', DateTime,default=datetime.datetime.now())

	# 分类多的一方
	product_class = relationship('Classify', backref=backref('fa_product'))

	# 发布管理员多的一方
	post_user = relationship('Manage', backref=backref('fa_product'))

	# 所属产品组多的一方
	hasteam = relationship('Team', backref=backref('fa_product'))

	# 颜色一的一方
	colors = relationship('ProColor', backref='fa_product', lazy='dynamic')

	# 洗涤说明多对多
	washs = relationship('Wash',secondary=pro_to_wash,
									backref=backref('fa_product', lazy='dynamic'),
									lazy='dynamic')
	# 推荐类型
	recommend = relationship('Recommend', backref=backref('fa_product'))

	# 一对一关联推荐封面图片
	covers_url = relationship('Images', backref=backref('fa_product'))

	def __repr__(self):
		return '<Product %r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r%r>' % (
			self.proid,
			self.pid,
			self.oldpid,
			self.creatorid,
			self.teamid,
			self.proname,
			self.price,
			self.text_centont,
			self.model_height,
			self.fabric,
			self.lining,
			self.wash,
			self.size_table,
			self.weights,
			self.the_net,
			self.first_order,
			self.again_order,
			self.shipping,
			self.flying,
			self.new_p,
			self.covers,
			self.place,
			self.colorid,
			self.size,
			self.display,
			self.add_time
		)

	# 推荐封面图片处理函数
	@hybrid_property
	def covers_split(self):
		if not self.covers_url:
			return []
		imgurl = self.covers_url.picurl.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	# 获取图片首图函数
	@hybrid_property
	def get_first_pic(self):
		if not self.colors:
			return []
		imgurl = ''
		clpic = ''
		for color in self.colors:
			for pic in color.colorpic:
				if pic.sort == None:
					clpic = pic.picurl
				if pic.sort == 0:
					clpic = pic.picurl
		imgurl = clpic.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	# 产品列表调用
	def to_list(self):
		return {
			'proid': self.proid,
			'pid': self.pid,
			'proname': self.proname,
			'price': self.price,
			'pro_pic': self.get_first_pic,
			'new_p': self.new_p,
			'covers': self.covers_split
		}

	# 得到尺码数组
	@hybrid_property
	def size_split(self):
		if not self.size:
			return []
		size = []
		size.append(self.size.split(','))
		return size

	# 得到洗涤说明
	@hybrid_property
	def get_wash(self):
		if not self.wash:
			return []
		wash = []
		washlist = Wash.query.filter(Wash.id.in_(self.wash))
		for wa in washlist:
			wash_json = {}
			wash_json["icon"] = Domain + wa.icon
			wash_json["text"] = wa.text
			wash.append(wash_json)
		return wash

	# 得到颜色的json数据
	@hybrid_property
	def get_colors(self):
		colorlist = self.colors
		if not colorlist:
			return []
		colors = []

		for model in colorlist:
			color_json = {}

			color_json["id"] = model.id
			color_json["color"] = model.color
			color_json["colortitle"] = model.colortitle
			color_json["number"] = model.number
			color_json["cover"] = Domain + model.cover
			picurl = []
			for pic in model.colorpic:
				pics = {}

				colorpic = pic.colorpic_split

				pics["sort"] = pic.sort
				pics["img"] = colorpic
				sorted(pics)

				picurl.append(pics)
			color_json["picurl"] = picurl
			sorted(color_json)
			colors.append(color_json)
		return colors

	# 获取商品详细信息
	def to_dict(self):
		return {
			'proid': self.proid,
			'proname': self.proname,
			'price': self.price,
			'text_centont': self.text_centont,
			'model_height': self.model_height,
			'fabric': self.fabric,
			'lining': self.lining,
			'size_table': self.size_table,
			'weights': self.weights,
			'wash': self.get_wash,
			'the_net': self.the_net,
			'first_order': self.first_order,
			'again_order': self.again_order,
			'shipping': self.shipping,
			'flying': self.flying,
			'new_p': self.new_p,
			'place': self.place,
			'size': self.size_split,
			'classname': self.product_class.classname,
			'procolor': self.get_colors
		}

# 资讯表
class News(Base):
	__tablename__ = 'fa_help'

	id = Column('id', Integer, primary_key=True)
	pid = Column('pid', Integer)
	title = Column('title', String(80), index = True)
	content = Column('content', String)
	display = Column('display',	SmallInteger)
	userid = Column('userid', Integer, ForeignKey(Manage.id))
	teamid = Column('teamid', Integer)
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())
	post_user = relationship('Manage', backref=backref('fa_help'))

	def __repr__(self):
		return '<News %r%r%r%r%r%r>' % (self.id, self.pid, self.title, self.content, self.display, self.addtime)

	# 帮助html编码转换
	@hybrid_property
	def change_html (self):
		if not self.content:
			return ''
		html_parser = HTMLParser.HTMLParser()
		html_con = self.content
		content = html_parser.unescape(html_con)
		return content

	# 获取帮助详细信息
	def to_list(self):
		return {
			'title': self.title,
			'content': self.change_html
		}

	# 得到内容里的图片
	@hybrid_property
	def get_imgs (self):
		if not self.content:
			return ''
		html_parser = HTMLParser.HTMLParser()
		html_con = self.content
		content = html_parser.unescape(html_con)

		picurl = re.findall('src="(.*?)"',content)
		piclist = []
		for p in range(len(picurl)):
			st = picurl[p].split('/')[-5:]
			se = '/'.join(st)
			piclist.append('%s%s%s' %(Domain,'/',se))

		piclist = piclist[0:3]

		return piclist

	# 获取新闻详细信息
	def to_newlist(self):
		return {
			'id': self.id,
			'title': self.title,
			'pic': self.get_imgs
		}


# 公司简介表
class Company(Base):
	__tablename__ = 'fa_company_intro'

	id = Column('id', Integer, primary_key=True, index=True)
	title = Column('title', String(80))
	content = Column('content', String)

	def __repr__(self):
		return '<Company %r%r%r>' % (self.id,self.title,self.content)

	# html编码转换
	@hybrid_property
	def change_html (self):
		if not self.content:
			return ''
		html_parser = HTMLParser.HTMLParser()
		html_con = self.content
		content = html_parser.unescape(html_con)
		return content

	# 前端调用函数
	def to_dict(self):
		return {
			'id': self.id,
			'title': self.title,
			'content': self.change_html
		}




# 轮显表
class Silder(Base):
	__tablename__ = 'fa_silder'

	id = Column('id', Integer, primary_key=True, index=True)
	title = Column('title', String(60))
	url = Column('url', Integer)
	picid = Column('picid', Integer, ForeignKey(Images.id))
	sort = Column('sort', SmallInteger)
	uptime = Column('uptime', DateTime,default=datetime.datetime.now())
	img_url = relationship('Images', backref=backref('fa_silder'))

	def __repr__(self):
		return '<Silder %r%r%r%r%r>' % (self.id, self.title, self.url, self.picid, self.uptime)

	# 图片处理函数
	@hybrid_property
	def actros_split(self):
		if not self.img_url.picurl:
			return []
		# return self.img_url.picurl.split(',')
		imgurl = self.img_url.picurl.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	# 前端调用函数
	def to_dict(self):
		return {
			'id': self.id,
			'title': self.title,
			'url': self.url,
			'img_url': self.actros_split,
			'sort': self.sort
		}


# 注册客户表
class Users(Base):
	__tablename__ = 'fa_user'

	id = Column('id', Integer, primary_key=True, index=True)
	phone = Column('phone', BigInteger)
	username = Column('username' , String(30))
	password = Column('password' , String(60))
	mail = Column('mail' , String(80))
	company = Column('company' , String(80))
	userpic = Column('userpic' , String(100))
	truename = Column('truename' , String(30))
	lock = Column('lock' , SmallInteger)
	verify = Column('verify' , SmallInteger)
	teamid = Column('teamid' , Integer, ForeignKey('fa_team.id'))
	touchid = Column('touchid' , String(60))
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())

	team = relationship("Team", back_populates="usersteam")

	# 一的一方关联订单
	hasorder = relationship("Order", uselist=False, back_populates="users")

	# 地址一的一方
	address = relationship('Address', backref='fa_user', lazy='dynamic')

	def __repr__(self):
		return '<Users %r%r%r%r%r%r%r%r>' % (self.id, self.phone, self.username, self.password, self.mail, self.company, self.userpic, self.truename )

# 客户收货地址表
class Address(Base):
	__tablename__ = 'fa_user_address'

	id = Column('id', Integer, primary_key=True)
	userid = Column('userid', Integer, ForeignKey('fa_user.id'), index=True)
	contacts = Column('contacts' , String(30))
	phone_number = Column('phone_number', BigInteger)
	address = Column('address' , String)
	default = Column('default' , SmallInteger)

	# 一的一方关联订单
	order_address = relationship("Order", uselist=False, back_populates="od_address")

	# 获取汉字首字母
	@hybrid_property
	def get_cn_first_letter(self,codec="UTF8"):
		if not self.contacts:
			return 'A'
		if codec!="GBK":
			if codec!="unicode":
				self.contacts=self.contacts.decode(codec)
			self.contacts=self.contacts.encode("GBK")

		if self.contacts<"\xb0\xa1" or self.contacts>"\xd7\xf9":
			return "X"
		if self.contacts<"\xb0\xc4":
			return "A"
		if self.contacts<"\xb2\xc0":
			return "B"
		if self.contacts<"\xb4\xed":
			return "C"
		if self.contacts<"\xb6\xe9":
			return "D"
		if self.contacts<"\xb7\xa1":
			return "E"
		if self.contacts<"\xb8\xc0":
			return "F"
		if self.contacts<"\xb9\xfd":
			return "G"
		if self.contacts<"\xbb\xf6":
			return "H"
		if self.contacts<"\xbf\xa5":
			return "J"
		if self.contacts<"\xc0\xab":
			return "K"
		if self.contacts<"\xc2\xe7":
			return "L"
		if self.contacts<"\xc4\xc2":
			return "M"
		if self.contacts<"\xc5\xb5":
			return "N"
		if self.contacts<"\xc5\xbd":
			return "O"
		if self.contacts<"\xc6\xd9":
			return "P"
		if self.contacts<"\xc8\xba":
			return "Q"
		if self.contacts<"\xc8\xf5":
			return "R"
		if self.contacts<"\xcb\xf9":
			return "S"
		if self.contacts<"\xcd\xd9":
			return "T"
		if self.contacts<"\xce\xf3":
			return "W"
		if self.contacts<"\xd1\x88":
			return "X"
		if self.contacts<"\xd4\xd0":
			return "Y"
		if self.contacts<"\xd7\xf9":
			return "Z"

	# 地址列表调用
	def to_list(self):
		return {
			'id': self.id,
			'contacts': self.contacts,
			'phone_number': self.phone_number,
			'address': self.address,
			'default': self.default,
			'pingying': self.get_cn_first_letter
		}


# 购物车表
class UserCart(Base):
	__tablename__ = 'fa_cart'

	id			 = Column('id', Integer, primary_key=True, index=True)
	order_type 	 = Column('order_type', SmallInteger)
	userid		 = Column('userid', Integer)
	proid		 = Column('proid', Integer, ForeignKey(Product.proid))
	pronumber	 = Column('pronumber' , String(30))
	size		 = Column('size' , String(10))
	color		 = Column('color' , String(10))
	unit		 = Column('unit' , Integer)
	price		 = Column('price' , Numeric)
	color_total  = Column('color_total' , Numeric)
	pic 		 = Column('pic' , String)

	# 调用产品多的一方
	products = relationship('Product', backref=backref('fa_cart'))

	# 购物车列表调用
	def to_list(self):
		return {
			'cartid': self.id,
			'order_type': self.order_type,
			'pronumber': self.pronumber,
			'size': self.size,
			'color': self.color,
			'unit': self.unit,
			'price': int(self.price),
			'color_total': int(self.color_total),
			'pic': self.pic,
			'proname': self.products.proname,
			'proid': self.proid
		}



# 订单表
class Order(Base):
	__tablename__ = 'fa_order'

	id			= Column('id', Integer, primary_key=True, index=True)
	number		= Column('number', String(30))
	userid		= Column('userid', Integer, ForeignKey('fa_user.id'))
	teamid		= Column('teamid', Integer)
	addressid   = Column('addressid', Integer, ForeignKey('fa_user_address.id'))
	state	    = Column('state', SmallInteger)
	order_total = Column('order_total', Numeric)
	order_type	= Column('order_type', SmallInteger)
	Logistical	= Column('Logistical', String(80))
	uptime		= Column('uptime', DateTime,default=datetime.datetime.now())
	addtime	    = Column('addtime', DateTime,default=datetime.datetime.now())

	# 多的一方关联订单所属客户
	users = relationship("Users", back_populates="hasorder")

	# 多的一方关联订单收货地址
	od_address = relationship("Address", back_populates="order_address")

	# 一的一方关联订单详细
	orderall = relationship("OrderDetailed", backref="fa_order", lazy='dynamic')

	# 一对一关联订单Excel
	orderexcel = relationship("OrderExcel", uselist=False, back_populates="order")

	# 订单状态附加一的一方
	orderstate = relationship('OrderState', backref='fa_order', lazy='dynamic')


	# 获取订单详细函数
	@hybrid_property
	def get_orderall(self):
		if not self.orderall:
			return []

		ordall = []
		for ods in self.orderall:
			ods_json = {}

			ods_json["id"] = ods.id
			ods_json["proid"] = ods.proid
			ods_json["proname"] = ods.products.proname
			ods_json["pronumber"] = ods.pronumber
			ods_json["size"] = ods.size
			ods_json["color"] = ods.color
			ods_json["unit"] = ods.unit
			ods_json["price"] = int(ods.price)
			ods_json["color_total"] = int(ods.color_total)
			ods_json["pic"] = ods.get_first_pic

			sorted(ods_json)
			ordall.append(ods_json)
		return ordall

	# 获得收货地址
	@hybrid_property
	def get_address(self):
		if not self.od_address:
			return {}
		address = {}
		address['contacts'] = str(self.od_address.contacts)
		address['phone_number'] = int(self.od_address.phone_number)
		address['address'] = self.od_address.address
		return address

	# 获取订单状态附加
	@hybrid_property
	def get_state_more(self):
		if not self.orderstate:
			return ''

		odstate = ''
		for s in self.orderstate:
			if self.state == s.state:
				odstate = str(s.text)
			if self.state == 6:
				odstate = s.text.split('|||')

		return odstate

	# 获取订单状态附加
	@hybrid_property
	def get_state_ls(self):
		if not self.orderstate:
			return []

		odstate = []
		for s in self.orderstate[::-1]:
			iss = {}
			iss['state'] = s.state
			iss['text'] = s.text
			iss['uptime'] = s.uptime
			if self.state == 6:
				iss['text'] = s.text.split('|||')
			odstate.append(iss)
		return odstate


	# 订单列表调用
	def to_list(self):
		return {
			'id': self.id,
			'number': self.number,
			'addressid': self.get_address,
			'state': self.state,
			'statemore': self.get_state_more,
			'order_total': int(self.order_total),
			'order_type': self.order_type,
			'uptime': self.uptime,
			'addtime': self.addtime,
			'orderall': self.get_orderall,
			'statelist': self.get_state_ls
		}


# 订单详细表
class OrderDetailed(Base):
	__tablename__ = 'order_other'

	id			 = Column('id', Integer, primary_key=True, index=True)
	proid		 = Column('proid', Integer, ForeignKey(Product.proid))
	pronumber	 = Column('pronumber' , String(30))
	size		 = Column('size' , String(10))
	color		 = Column('color' , String(10))
	unit		 = Column('unit' , Integer)
	price		 = Column('price' , Numeric)
	color_total	 = Column('color_total' , Numeric)
	order_id	 = Column('order_id' , Integer, ForeignKey('fa_order.id'))

	# 调用产品多的一方
	products = relationship('Product', backref=backref('order_other'))

	# 获取图片首图函数
	@hybrid_property
	def get_first_pic(self):
		if not self.products.colors:
			return []
		imgurl = ''
		clpic = ''
		for color in self.products.colors:
			for pic in color.colorpic:
				if pic.sort == None:
					clpic = pic.picurl
				if pic.sort == 0:
					clpic = pic.picurl
		imgurl = clpic.split(',')
		imgurls = ''
		for i in range(len(imgurl)):
			imgurls = '%s%s' %(Domain,imgurl[3])
		return imgurls

# 订单Excel路径保存表
class OrderExcel(Base):
	__tablename__ = 'fa_order_excel'

	id			 = Column('id', Integer, primary_key=True)
	orderid		 = Column('orderid', Integer, ForeignKey('fa_order.id'), index=True)
	excelpath	 = Column('excelpath' , String)
	# 一对一关联订单Excel
	order = relationship("Order", back_populates="orderexcel")

# 订单状态附加表
class OrderState(Base):
	__tablename__ = 'fa_order_state'

	id		 = Column('id', Integer, primary_key=True)
	orderid	 = Column('orderid', Integer, ForeignKey('fa_order.id'), index=True)
	state	 = Column('state' , SmallInteger)
	text	 = Column('text' , String)
	uptime   = Column('uptime' , DateTime,default=datetime.datetime.now())


# 联系我们表
class ContactUs(Base):
	__tablename__ = 'fa_contactus'

	id = Column('id', Integer, primary_key=True, index=True)
	department = Column('department', String(30))
	title = Column('title', String(30))
	name = Column('name', String(10))
	phone = Column('phone', BigInteger)
	mail = Column('mail', String(100))
	wechat = Column('wechat', String(50))
	sort = Column('sort', SmallInteger)

	def __repr__(self):
		return '<ContactUs %r%r%r%r%r%r%r%r>' % (self.id,self.department,self.title,self.name,self.phone,self.mail,self.wechat,self.sort)


# 留言表
class Guestbook(Base):
	__tablename__ = 'fa_guestbook'

	id = Column('id', Integer, primary_key=True, index=True)
	content = Column('content',	String)
	userid = Column('userid', Integer, ForeignKey(Users.id))
	addtime = Column('addtime', DateTime,default=datetime.datetime.now())

	# 多的一方 关联产品的分类
	users = relationship('Users', backref=backref('fa_guestbook'))

	# 消息已读一的一方
	reads = relationship('MuGb', backref='fa_guestbook', lazy='dynamic')

	def __repr__(self):
		return '<Guestbook %r%r%r%r>' % (Guestbook.id, Guestbook.content, Guestbook.userid, Guestbook.addtime)

# 管理员阅读留言关联表
class MuGb(Base):
	__tablename__ = 'gbook_muser'

	id = Column('id', Integer, primary_key=True, index=True)
	manageid = Column('manageid',	Integer, ForeignKey('fa_manage.id'))
	bookid = Column('bookid', Integer, ForeignKey('fa_guestbook.id'), index=True)
	status = Column('status',	SmallInteger)

	def __repr__(self):
		return '<MuGb %r%r%r%r>' % (MuGb.id, MuGb.manageid, MuGb.bookid, MuGb.status)

# 用户喜欢产品表
class UserLike(Base):
	__tablename__ = 'fa_like_product'

	id = Column('id', Integer, primary_key=True)
	like_porid = Column('like_porid',	Integer, ForeignKey(Product.proid))
	user_id = Column('user_id', Integer, ForeignKey('fa_user.id'), index=True)
	add_time = Column('add_time', DateTime,default=datetime.datetime.now())

	# 调用产品多的一方
	products = relationship('Product', backref=backref('fa_like_product'))

	# 获取图片首图函数
	@hybrid_property
	def get_first_pic(self):
		if not self.colors:
			return []
		imgurl = ''
		clpic = ''
		for color in self.colors:
			for pic in color.colorpic:
				if pic.sort == None:
					clpic = pic.picurl
				if pic.sort == 0:
					clpic = pic.picurl
		imgurl = clpic.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls

	# 获取图片首图函数
	@hybrid_property
	def get_first_pic(self):
		if not self.products.colors:
			return []
		imgurl = ''
		clpic = ''
		for color in self.products.colors:
			for pic in color.colorpic:
				if pic.sort == None:
					clpic = pic.picurl
				if pic.sort == 0:
					clpic = pic.picurl
		imgurl = clpic.split(',')
		imgurls = []
		for i in range(len(imgurl)):
			imgurls.append(Domain + imgurl[i])
		return imgurls


	# 产品列表调用
	def to_list(self):
		return {
			'pid': self.products.pid,
			'price': self.products.price,
			'proid': self.products.proid,
			'proname': self.products.proname,
			'pro_pic': self.get_first_pic
		}

if __name__ == '__main__':
	Base.metadata.create_all(engine)
