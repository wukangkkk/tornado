#cdoing=utf-8
import os
from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler
from handlers import Passport,VerifyCode
from handlers import Profile,House
handlers=[
    (r"/api/register",Passport.RegisterHandler),
    (r"/api/piccode",VerifyCode.PicCodeHandler),
    (r"/api/smscode",VerifyCode.SMSCodeHandler),
    (r"/api/check_login",Passport.CheckLoginHandler),
    (r"/api/logout",Passport.LogoutHandler),
    (r"/api/login",Passport.LoginHandler),
    (r"/api/profile",Profile.ProfileHandler),
    (r"/api/profile/avatar", Profile.AvatarHandler),
    (r"/api/profile/auth",Profile.AuthHandler),
    (r"/api/profile/name",Profile.NameHandler),
    (r"/api/house/area",House.AreaInfoHandler),
    (r'^/api/house/my$', House.MyHousesHandler),
    (r'^/api/house/image$', House.HouseImageHandler),
    (r"/api/house/info",House.HouseInfoHandler),
    (r'^/api/house/index$', House.IndexHandler),
    (r'^/api/house/list$', House.HouseListHandler),
    (r'^/api/house/list2$', House.HouseListRedisHandler),
    (r"/(.*)", StaticFileHandler,dict(path=os.path.join(os.path.dirname(__file__),
                                    "html"), default_filename="index.html"))
]