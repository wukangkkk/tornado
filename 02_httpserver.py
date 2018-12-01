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
	http_server.listen(8000)
	tornado.ioloop.IOLoop.current().start()


    
