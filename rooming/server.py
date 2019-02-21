#coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import torndb
import redis
from urls import handlers
from tornado.options import options,define
import config
define("port",type=int,default=8000,help="run the server on the given port")

class Application(tornado.web.Application):
    """
    数据库的创建，一定要记住
    """
    def __init__(self,*args,**kwargs):
        super(Application,self).__init__(*args,**kwargs)
        # self.db=torndb.Connection(
        #     host=config.mysql_options["host"],
        #     database=config.mysql_options["database"],
        #     user=config.mysql_options["user"],
        #     password=config.mysql_options["password"]
        # )
        #字典解包
        self.db=torndb.Connection(**config.mysql_options)
        # self.redis=redis.StrictRedis(
        #     host=config.redis_options["host"],
        #     port=config.redis_options["port"]
        # )
        self.redis=redis.StrictRedis(**config.redis_options)

def main():
    #options.logging=config.log_level
    #options.log_file_prefix=config.log_file
    tornado.options.parse_command_line()
    app=Application(handlers,**config.settings
                                )
    http_server=tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
if __name__=='__main__':
    main()