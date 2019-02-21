#coding=utf-8
import os
settings={
    "static_path":os.path.join(os.path.dirname(__file__),'static'),
    "template":os.path.join(os.path.dirname(__file__),'template'),
    "debug":True,
    "cookie_secret":'jkLpQ498TLKLZxeLSEDNpAH4bfh8JkjdoNKtwVPP15w=',
    "xsrf_cookies":True,

}

mysql_options=dict(
    host="127.0.0.1",
    database="itcast",
    user="root",
    password="mysql"
)

redis_options=dict(
    host="127.0.0.1",
    port=6379
)
log_file=os.path.join(os.path.dirname(__file__),'logs/log')
log_level="debug"

# 密码加密密钥
passwd_hash_key = "nlgCjaTXQX2jpupQFQLoQo5N4OkEmkeHsHD9+BBx2WQ="