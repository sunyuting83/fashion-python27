# coding:utf-8
from flask import Blueprint

# 解决中文显示问题
import sys
import imp
imp.reload(sys)

api = Blueprint('manage', __name__, static_folder='../static')



from . import view, public, admin, admin_group, admin_team, classify, company, contactus, manage_news, manage_product, silder, sys_config, wash, size, manage_order, manage_customers, manage_guestbook, uploader, recommend