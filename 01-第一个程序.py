#coding=utf-8

import tornado.web
import tornado.ioloop
class IndexHandle(tornado.web.RequestHandler):

	def get(self):
	    """定义请求函数"""
	    self.write('hello wukang')


if __name__ == '__main__':
    app=tornado.web.Application([
            (r'/',IndexHandle),
                              ])
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()