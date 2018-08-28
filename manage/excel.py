# coding:utf-8
from model import OrderExcel, db_session
import datetime
import os
import xlwt
import time
import json

def getFilePath():
	# 获取文件完整路径
	nowtime = time.strftime("%Y%m%d")
	backdir = "static/order/"
	exceldir = backdir + nowtime +"/"
	if not os.path.exists(exceldir):
	    os.makedirs(exceldir)
	else:
	    pass
	return exceldir

def get_first_pic(products):
	if not products.colors:
		return ''
	for color in products.colors:
		for pic in color.colorpic:
			if pic.sort == None:
				clpic = pic.picurl
			if pic.sort == 0:
				clpic = pic.picurl
	imgurl = clpic.split(',')
	imgurls = ''
	for i in range(len(imgurl)):
		imgurls = imgurl[3]
	return imgurls

def set_style(name,height,bold=False,center=False):

	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_CENTER
	alignment.vert = xlwt.Alignment.VERT_CENTER


	style = xlwt.XFStyle() # 初始化样式
 
	font = xlwt.Font() # 为样式创建字体
	font.name = name # 'Times New Roman'
	font.bold = bold
	font.color_index = 4
	font.height = height

	if center is True:
		style.alignment = alignment
 
	# borders= xlwt.Borders()
	# borders.left= 6
	# borders.right= 6
	# borders.top= 6
	# borders.bottom= 6
 
	style.font = font
	# style.borders = borders
 
	return style
 
 
#写excel
def write_excel(self):
	f = xlwt.Workbook() #创建工作簿
 
	'''
	创建第一个sheet:
		sheet1
	'''
	sheet1 = f.add_sheet(u'订单明细表',cell_overwrite_ok=True) #创建sheet

	product = [u'产品图片',u'产品名称',u'产品编号',u'颜色',u'尺码',u'数量',u'单价',u'尺码总价']
	
	propic = []
	proname = []
	pronumber = []
	procolor = []
	prosize = []
	prounit = []
	proprice = []
	color_total = []
	for ords in self.orderall:
		propic.append(get_first_pic(ords.products))
		proname.append(ords.products.proname)
		pronumber.append(ords.pronumber)
		procolor.append(ords.color)
		prosize.append(ords.size)
		prounit.append(ords.unit)
		proprice.append(ords.price)
		color_total.append(ords.color_total)
 	
 	sheet1.write_merge(0,0,0,6,u'订单明细表',set_style('Microsoft YaHei',310,False,True))

 	sheet1.write_merge(1,1,0,6,u'',set_style('Microsoft YaHei',220,False))

 	#生成订单编号
	sheet1.write_merge(2,2,0,1,u'订单编号：',set_style('Microsoft YaHei',220,True))
	sheet1.write_merge(2,2,2,6,self.number,set_style('Microsoft YaHei',220,True))

 	sheet1.write_merge(3,3,0,6,u'',set_style('Microsoft YaHei',220,False))

 	sheet1.write_merge(4,4,0,6,u'客户信息',set_style('Microsoft YaHei',220,True))
 	'''
 	客户表头
 	'''
 	sheet1.write_merge(5,5,0,2,u'下单客户：',set_style('Microsoft YaHei',220,False))
 	sheet1.write_merge(5,5,3,4,u'联系人',set_style('Microsoft YaHei',220,False,True))
 	sheet1.write_merge(5,5,5,6,u'联系电话',set_style('Microsoft YaHei',220,False,True))
	'''
 	客户信息
 	'''
 	sheet1.write_merge(6,6,0,2,self.users.company,set_style('Microsoft YaHei',220,False))
 	sheet1.write_merge(6,6,3,4,self.users.truename,set_style('Microsoft YaHei',220,False,True))
 	sheet1.write_merge(6,6,5,6,self.users.phone,set_style('Microsoft YaHei',220,False,True))

 	sheet1.write_merge(7,7,0,6,u'',set_style('Microsoft YaHei',220,False))

 	sheet1.write_merge(8,8,0,6,u'收货地址：',set_style('Microsoft YaHei',220,True))
 	sheet1.write_merge(9,9,0,2,u'联系人：'+self.od_address.contacts,set_style('Microsoft YaHei',220,False))
 	sheet1.write_merge(9,9,3,6,u'联系电话：'+str(self.od_address.phone_number),set_style('Microsoft YaHei',220,False))
 	sheet1.write_merge(10,10,0,6,u'收货地址：'+self.od_address.address,set_style('Microsoft YaHei',220,False))

 	sheet1.write_merge(11,11,0,6,u'',set_style('Microsoft YaHei',220,False))

 	sheet1.write_merge(12,12,0,6,u'订单产品信息列表：',set_style('Microsoft YaHei',220,True))

 	for i in range(0,len(product)):
		sheet1.write(13,i,product[i],set_style('Microsoft YaHei',220,False))

	for i in range(0,len(proname)):
		sheet1.write(i+14,0,proname[i],set_style('Microsoft YaHei',220))
	for i in range(0,len(pronumber)):
		sheet1.write(i+14,1,pronumber[i],set_style('Times New Roman',220))
	for i in range(0,len(procolor)):
		sheet1.write(i+14,2,procolor[i],set_style('Microsoft YaHei',220))
	for i in range(0,len(prosize)):
		sheet1.write(i+14,3,prosize[i],set_style('Times New Roman',220))
	for i in range(0,len(prounit)):
		sheet1.write(i+14,4,prounit[i],set_style('Times New Roman',220))
	for i in range(0,len(proprice)):
		sheet1.write(i+14,5,proprice[i],set_style('Times New Roman',220))
	for i in range(0,len(color_total)):
		sheet1.write(i+14,6,color_total[i],set_style('Times New Roman',220))
	last = len(color_total)

	sheet1.write_merge(last+15,last+15,0,3,u'下单时间：'+str(self.addtime),set_style('Microsoft YaHei',220,True))
	sheet1.write_merge(last+15,last+15,4,7,u'订单总价：'+str(self.order_total),set_style('Microsoft YaHei',220,True))

	path = getFilePath()
	fullpath = '%s%s%s' %(path,self.number,'.xls')
	filename = '%s%s' %(self.number,'.xls')

	f.save(fullpath) #保存文件

	# 入库操作
	add_excel = OrderExcel(orderid = self.id, excelpath = fullpath)
	db_session.add(add_excel)

	try:
		db_session.commit()
	except Exception as e:
		print e
		db_session.rollback()
		return json.dumps({'code': 0, 'message': '添加失败'})

	return json.dumps({'code':1, 'fullpath':fullpath, 'filename':filename})