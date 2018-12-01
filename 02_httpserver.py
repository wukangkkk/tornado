#coding=utf-8
import tornado.web
import tornado.ioloop
#引入httpserver新模块
import tornado.httpserver
class IndexHandler(tornado.web.RequestHandler):
	"""主路由器处理"""
	def get(self):
		self.write('hellow world')

if __name__ == '__main__':
	app=tornado.web.Application([
	            (r"/",IndexHandler),                
	                            ])
	http_server=tornado.httpserver.HTTPServer(app)
	#修改成多进程
	#http_server.listen(8000)
	# http_server.start(num_processes=1)方法指定开启几个进程，参数num_processes默认值为1，即默认仅开启一个进程；如果num_processes为None或者<=0，则自动根据机器硬件的cpu核芯数创建同等数目的子进程；如果num_processes>0，则创建num_processes个子进程
	http_server.bind(8000)
	http_server.start(0)
	tornado.ioloop.IOLoop.current().start()


    
