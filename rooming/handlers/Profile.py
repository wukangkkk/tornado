#coding=utf-8
import logging
import constants
from handlers.BaseHandler import BaseHandler
from utils.response_code import RET
from utils.commom import required_login
from utils.qiniu_storage import storage
class AvatarHandler(BaseHandler):
    """上传图片"""
    @required_login
    def post(self):
        files=self.request.files.get("avatar")
        if not files:
            return self.write(dict(errcode=RET.PARAMERR,errmsg="图片未传"))
        avatar=files[0]["body"]
        #调用七牛传照片
        try:
            file_name=storage(avatar)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.THIRDERR,errmsg="图片上传失败"))
        #从session取出user_id
        user_id=self.session.data["user_id"]
        # 保存图片名（即图片url）到数据中
        sql="update ih_user_profile set up_avatar=%(avatar)s where up_user_id=%(user_id)s"

        try:
            row_count = self.db.execute_rowcount(sql, avatar=file_name, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="保存错误"))
        self.write(dict(errcode=RET.OK, errmsg="保存成功", data="%s%s" % (constants.QINIU_URL_PREFIX, file_name)))



class ProfileHandler(BaseHandler):
    @required_login
    def get(self):
        """个人信息获取刷新"""
        user_id=self.session.data["user_id"]
        try:
            ret=self.db.get("select up_name,up_mobile,up_avatar from ih_user_profile WHERE up_user_id=%s",user_id)

        except Exception as e:
            logging.error(e)
            return self.write({"errcode":RET.DBERR,"errmsg":"get data error"})
        if ret["up_avatar"]:
            img_url=constants.QINIU_URL_PREFIX+ret["up_avatar"]
        else:
            img_url=None
        self.write({"errcode":RET.OK,"errmsg":'OK',
                          "data":{"user_id":user_id,"name":ret["up_name"],"mobile":
                                  ret["up_mobile"],"avatar":img_url}})

class NameHandler(BaseHandler):
    @required_login
    def post(self):
        """用户名修改"""
        #获取用户名的id
        user_id=self.session.data["user_id"]
        #获取用户名的名字
        name=self.json_args.get("name")
        if name in (None,""):
            return self.write({"errcode":RET.PARAMERR,"errmsg":"param error"})
        #把修改的名字保存在mysql数据当中
        try:
            self.db.execute_rowcount("update ih_user_profile set up_name=%s WHERE up_user_id=%s",name,user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"ercode":RET.DBERR,"errmsg":"database error!"})
        #修改session数据，并保存
        self.session.data["name"]=name
        try:
            self.session.save()
        except Exception as e:
            logging.error(e)
        return self.write({"errcode":RET.OK,"errmsg":"OK"})


class AuthHandler(BaseHandler):
    """实名认证"""
    @required_login
    def get(self):
        #获取用户的user_id
        user_id=self.session.data["user_id"]
        #在数据库中查找
        try:
            ret=self.db.get("select up_real_name,up_id_card from ih_user_profile WHERE up_user_id=%s",user_id)
        except Exception as e:
            #数据库出错
            logging.error(e)
            return self.write({"errcode":RET.DBERR,"errmsg":"get error in database!"})
        logging.debug(ret)
        if not ret:
            return self.write({"errcode":RET.NODATA,"errmsg":"no data"})
        self.write({"errcode":RET.OK,"errmsg":"OK","data":{"real_name":ret.get("up_real_name",""),
                                                           "id_card":ret.get("up_id_card","")}})
    @required_login
    def post(self):
        user_id=self.session.data["user_id"]
        real_name=self.json_args.get("real_name")
        id_card=self.json_args.get("id_card")
        if real_name in (None,"") or id_card in (None,""):
            return self.write({"errcode":RET.PARAMERR,"errmsg":"param error"})
        #判断身份证号是否正确
        try:
            self.db.execute_rowcount("update ih_user_profile set up_real_name=%s,up_id_card=%s WHERE up_user_id=%s",real_name,id_card,user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode":RET.DBERR,"errmsg":"up data failed!"})
        self.write({"errcode":RET.OK,"errmsg":"OK"})

class IndexHandler(BaseHandler):
    """主页信息"""
    def get(self):
        try:
            ret = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            json_houses = ret
        else:
            try:
                # 查询数据库，返回房屋订单数目最多的5条数据(房屋订单通过hi_order_count来表示）
                house_ret = self.db.query("select hi_house_id,hi_title,hi_order_count,hi_index_image_url from ih_house_info " \
                                          "order by hi_order_count desc limit %s;" % constants.HOME_PAGE_MAX_HOUSES)
            except Exception as e:
                logging.error(e)
                return self.write({"errcode":RET.DBERR, "errmsg":"get data error"})
            if not house_ret:
                return self.write({"errcode":RET.NODATA, "errmsg":"no data"})
            houses = []
            for l in house_ret:
                if not l["hi_index_image_url"]:
                    continue
                house = {
                    "house_id":l["hi_house_id"],
                    "title":l["hi_title"],
                    "img_url": constants.QINIU_URL_PREFIX + l["hi_index_image_url"]
                }
                houses.append(house)
            json_houses = json.dumps(houses)
            try:
                self.redis.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, json_houses)
            except Exception as e:
                logging.error(e)

        # 返回首页城区数据
        try:
            ret = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            json_areas = ret
        else:
            try:
                area_ret = self.db.query("select ai_area_id,ai_name from ih_area_info")
            except Exception as e:
                logging.error(e)
                area_ret = None
            areas = []
            if area_ret:
                for area in area_ret:
                    areas.append(dict(area_id=area["ai_area_id"], name=area["ai_name"]))
            json_areas = json.dumps(areas)
            try:
                self.redis.setex("area_info", constants.REDIS_AREA_INFO_EXPIRES_SECONDES, json_areas)
            except Exception as e:
                logging.error(e)
        resp = '{"errcode":"0", "errmsg":"OK", "houses":%s, "areas":%s}' % (json_houses, json_areas)
        self.write(resp)


class HouseListHandler(BaseHandler):
    """房源列表页面"""
    def get(self):
        """get方式用来获取数据库数据，本身的逻辑不会对数据库数据产生影响"""
        """
        传入参数说明
        start_date 用户查询的起始时间 sd     非必传   ""          "2017-02-28"
        end_date    用户查询的终止时间 ed    非必传   ""
        area_id     用户查询的区域条件   aid 非必传   ""
        sort_key    排序的关键词     sk     非必传   "new"      "new" "booking" "price-inc"  "price-des"
        page        返回的数据页数     p     非必传   1
        """
        # 获取参数
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        area_id = self.get_argument("aid", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")

        # 检查参数
        # 判断日期格式、sort_Key 字段的值、page的整数

        # 数据查询
        # 涉及到表： ih_house_info 房屋的基本信息  ih_user_profile 房东的用户信息 ih_order_info 房屋订单数据

        sql = "select distinct hi_title,hi_house_id,hi_price,hi_room_count,hi_address,hi_order_count,up_avatar,hi_index_image_url,hi_ctime" \
              " from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id left join ih_order_info" \
              " on hi_house_id=oi_house_id"

        sql_total_count = "select count(distinct hi_house_id) count from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id " \
                          "left join ih_order_info on hi_house_id=oi_house_id"

        sql_where = [] # 用来保存sql语句的where条件
        sql_params = {} # 用来保存sql查询所需的动态数据

        if start_date and end_date:
            sql_part = "((oi_begin_date>%(end_date)s or oi_end_date<%(start_date)s) " \
                       "or (oi_begin_date is null and oi_end_date is null))"
            sql_where.append(sql_part)
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_part = "(oi_end_date<%(start_date)s or (oi_begin_date is null and oi_end_date is null))"
            sql_where.append(sql_part)
            sql_params["start_date"] = start_date
        elif end_date:
            sql_part = "(oi_begin_date>%(end_date)s or (oi_begin_date is null and oi_end_date is null))"
            sql_where.append(sql_part)
            sql_params["end_date"] = end_date

        if area_id:
            sql_part = "hi_area_id=%(area_id)s"
            sql_where.append(sql_part)
            sql_params["area_id"] = area_id

        if sql_where:
            sql += " where "
            sql += " and ".join(sql_where)

        # 有了where条件，先查询总条目数
        try:
            ret = self.db.get(sql_total_count, **sql_params)
        except Exception as e:
            logging.error(e)
            total_page = -1
        else:
            total_page = int(math.ceil(ret["count"] / float(constants.HOUSE_LIST_PAGE_CAPACITY)))
            page = int(page)
            if page>total_page:
                return self.write(dict(errcode=RET.OK, errmsg="OK", data=[], total_page=total_page))

        # 排序
        if "new" == sort_key: # 按最新上传时间排序
            sql += " order by hi_ctime desc"
        elif "booking" == sort_key: # 最受欢迎
            sql += " order by hi_order_count desc"
        elif "price-inc" == sort_key: # 价格由低到高
            sql += " order by hi_price asc"
        elif "price-des" == sort_key: # 价格由高到低
            sql += " order by hi_price desc"

        # 分页
        # limit 10 返回前10条
        # limit 20,3 从20条开始，返回3条数据
        if 1 == page:
            sql += " limit %s" % constants.HOUSE_LIST_PAGE_CAPACITY
        else:
            sql += " limit %s,%s" % ((page-1)*constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY)

        logging.debug(sql)
        try:
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询出错"))
        data = []
        if ret:
            for l in ret:
                house = dict(
                    house_id=l["hi_house_id"],
                    title=l["hi_title"],
                    price=l["hi_price"],
                    room_count=l["hi_room_count"],
                    address=l["hi_address"],
                    order_count=l["hi_order_count"],
                    avatar=constants.QINIU_URL_PREFIX+l["up_avatar"] if l.get("up_avatar") else "",
                    image_url=constants.QINIU_URL_PREFIX+l["hi_index_image_url"] if l.get("hi_index_image_url") else ""
                )
                data.append(house)
        self.write(dict(errcode=RET.OK, errmsg="OK", data=data, total_page=total_page))


class HouseListRedisHandler(BaseHandler):
    """使用了缓存的房源列表页面"""
    def get(self):
        """get方式用来获取数据库数据，本身的逻辑不会对数据库数据产生影响"""
        """
        传入参数说明
        start_date 用户查询的起始时间 sd     非必传   ""          "2017-02-28"
        end_date    用户查询的终止时间 ed    非必传   ""
        area_id     用户查询的区域条件   aid 非必传   ""
        sort_key    排序的关键词     sk     非必传   "new"      "new" "booking" "price-inc"  "price-des"
        page        返回的数据页数     p     非必传   1
        """
        # 获取参数
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        area_id = self.get_argument("aid", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")

        # 检查参数
        # 判断日期格式、sort_Key 字段的值、page的整数

        # 先从redis中获取数据
        try:
            redis_key = "houses_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
            ret = self.redis.hget(redis_key, page)
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            logging.info("hit redis")
            return self.write(ret)


        # 数据查询
        # 涉及到表： ih_house_info 房屋的基本信息  ih_user_profile 房东的用户信息 ih_order_info 房屋订单数据

        sql = "select distinct hi_title,hi_house_id,hi_price,hi_room_count,hi_address,hi_order_count,up_avatar,hi_index_image_url,hi_ctime" \
              " from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id left join ih_order_info" \
              " on hi_house_id=oi_house_id"

        sql_total_count = "select count(distinct hi_house_id) count from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id " \
                          "left join ih_order_info on hi_house_id=oi_house_id"

        sql_where = [] # 用来保存sql语句的where条件
        sql_params = {} # 用来保存sql查询所需的动态数据

        if start_date and end_date:
            sql_part = "((oi_begin_date>%(end_date)s or oi_end_date<%(start_date)s) " \
                       "or (oi_begin_date is null and oi_end_date is null))"
            sql_where.append(sql_part)
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_part = "(oi_end_date<%(start_date)s or (oi_begin_date is null and oi_end_date is null))"
            sql_where.append(sql_part)
            sql_params["start_date"] = start_date
        elif end_date:
            sql_part = "(oi_begin_date>%(end_date)s or (oi_begin_date is null and oi_end_date is null))"
            sql_where.append(sql_part)
            sql_params["end_date"] = end_date

        if area_id:
            sql_part = "hi_area_id=%(area_id)s"
            sql_where.append(sql_part)
            sql_params["area_id"] = area_id

        if sql_where:
            sql += " where "
            sql += " and ".join(sql_where)

        # 有了where条件，先查询总条目数
        try:
            ret = self.db.get(sql_total_count, **sql_params)
        except Exception as e:
            logging.error(e)
            total_page = -1
        else:
            total_page = int(math.ceil(ret["count"] / float(constants.HOUSE_LIST_PAGE_CAPACITY)))
            page = int(page)
            if page>total_page:
                return self.write(dict(errcode=RET.OK, errmsg="OK", data=[], total_page=total_page))

        # 排序
        if "new" == sort_key: # 按最新上传时间排序
            sql += " order by hi_ctime desc"
        elif "booking" == sort_key: # 最受欢迎
            sql += " order by hi_order_count desc"
        elif "price-inc" == sort_key: # 价格由低到高
            sql += " order by hi_price asc"
        elif "price-des" == sort_key: # 价格由高到低
            sql += " order by hi_price desc"

        # 分页
        # limit 10 返回前10条
        # limit 20,3 从20条开始，返回3条数据
        if 1 == page:
            sql += " limit %s" % (constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_PAGE_CACHE_NUM)
        else:
            sql += " limit %s,%s" % ((page-1)*constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_PAGE_CACHE_NUM)

        logging.debug(sql)
        try:
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询出错"))
        data = []
        if ret:
            for l in ret:
                house = dict(
                    house_id=l["hi_house_id"],
                    title=l["hi_title"],
                    price=l["hi_price"],
                    room_count=l["hi_room_count"],
                    address=l["hi_address"],
                    order_count=l["hi_order_count"],
                    avatar=constants.QINIU_URL_PREFIX+l["up_avatar"] if l.get("up_avatar") else "",
                    image_url=constants.QINIU_URL_PREFIX+l["hi_index_image_url"] if l.get("hi_index_image_url") else ""
                )
                data.append(house)

        # 对与返回的多页面数据进行分页处理
        # 首先取出用户想要获取的page页的数据
        current_page_data = data[:constants.HOUSE_LIST_PAGE_CAPACITY]
        house_data = {}
        house_data[page] = json.dumps(dict(errcode=RET.OK, errmsg="OK", data=current_page_data, total_page=total_page))
        # 将多取出来的数据分页
        i = 1
        while 1:
            page_data = data[i*constants.HOUSE_LIST_PAGE_CAPACITY: (i+1)*constants.HOUSE_LIST_PAGE_CAPACITY]
            if not page_data:
                break
            house_data[page+i] = json.dumps(dict(errcode=RET.OK, errmsg="OK", data=page_data, total_page=total_page))
            i += 1
        try:
            redis_key = "houses_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
            self.redis.hmset(redis_key, house_data)
            self.redis.expire(redis_key, constants.REDIS_HOUSE_LIST_EXPIRES_SECONDS)
        except Exception as e:
            logging.error(e)

        self.write(house_data[page])




