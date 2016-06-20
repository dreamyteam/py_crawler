#-*- coding:utf-8 -*-

import random
from settings import *

class MyUserAgent(object):
	def process_request(self, request, spider):
		request.headers.setdefault('User-Agent', random.choice(USER_AGENTS))



