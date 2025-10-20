# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-08-12 09:06:24
@LastEditTime: 2025-06-04 16:51:42
@LastEditors: HuangJianYi
:description: 淘宝top接口基础类
"""
from seven_cloudapp_frame.libs.common import *
from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper
from seven_top import top
from seven_cloudapp_frame.models.db_models.base.base_info_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.seven_model import *

class TopBaseModel():
    """
    :description: 淘宝top接口业务模型
    """
    def __init__(self, context=None, logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def instantiate(self, app_id, user_nick, access_token, app_key, app_secret, is_log=False, main_user_open_id='', app_name='', description='', icon="", template_id='', template_version='', is_instance=1):
        """
        :description: 实例化
        :param app_id:应用标识
        :param user_nick:用户昵称
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :param main_user_open_id：main_user_open_id
        :param app_name：应用名称
        :param description：应用描述
        :param icon：应用图标
        :param template_id：模板ID
        :param template_version：模板版本号
        :param is_instance：实例化类型(0-未实例化 1-主实例化 2-关联实例化)
        :return
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        base_info = BaseInfoModel(context=self.context).get_entity()
        if not base_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "基础信息未配置"
            return invoke_result_data
        app_name = base_info.product_name if not app_name else app_name
        description = base_info.product_desc if not description else description
        icon = base_info.product_icon if not icon else icon
        template_id = share_config.get_value("client_template_id") if not template_id else template_id
        template_version = base_info.client_ver if not template_version else template_version
        app_info_model = AppInfoModel(context=self.context)
        app_info = None
        is_change_project_code = False #是否改变了项目代码，用于判断是否进行了服务市场套餐的改变,第一次实例化默认False

        # 产品千牛后台GM工具（运营人员模拟登录）
        if app_id:
            app_info = app_info_model.get_entity(where="app_id=%s", params=app_id)
            if app_info:
                invoke_result_data.data = {"app_id": app_info.app_id, "store_user_nick": app_info.store_user_nick, "user_nick": app_info.store_user_nick, "access_token": app_info.access_token, "seller_id":app_info.seller_id}
                return invoke_result_data
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，该店铺未实例化。"
            return invoke_result_data

        if not user_nick:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起,请先授权登录"
            return invoke_result_data
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起,请先授权登录"
            return invoke_result_data
        app_info = app_info_model.get_entity(where="store_user_nick=%s and template_id=%s", params=[store_user_nick, template_id])
        # 有效时间获取
        invoke_result_data = self.get_dead_date(store_user_nick, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return invoke_result_data
        dead_date = invoke_result_data.data
        project_code = self.get_project_code(store_user_nick, access_token, app_key, app_secret, is_log)
        if app_info:
            if main_user_open_id !="" and app_info.main_user_open_id == "":
                app_info.main_user_open_id = main_user_open_id
            if dead_date != "expire":
                app_info.expiration_date = dead_date
            if project_code != "":
                if project_code != app_info.project_code:
                    is_change_project_code = True
                app_info.project_code = project_code
            # invoke_result_data = self.get_goods_list(0, 1, "", "", "", access_token, app_key, app_secret)
            invoke_result_data = self.get_shop(access_token, app_key, app_secret, is_log)
            if invoke_result_data.success == True:
                app_info.access_token = access_token
                shop_info = invoke_result_data.data            
                if "shop_seller_get_response" in shop_info.keys():
                    app_info.store_name = shop_info["shop_seller_get_response"]["shop"]["title"]
                    app_info.store_icon = shop_info["shop_seller_get_response"]["shop"]["pic_path"] if "https:" in shop_info["shop_seller_get_response"]["shop"]["pic_path"] or "//gw.alicdn.com" in shop_info["shop_seller_get_response"]["shop"]["pic_path"]  else "http://logo.taobao.com/shop-logo" + shop_info["shop_seller_get_response"]["shop"]["pic_path"]
                
            app_info_model.update_entity(app_info, "main_user_open_id,expiration_date,project_code,access_token,store_name,store_icon")
            app_info_model.delete_dependency_key(DependencyKey.app_info(app_info.app_id))
            invoke_result_data.data = {"app_id": app_info.app_id, "store_user_nick": app_info.store_user_nick, "user_nick": user_nick, "access_token": app_info.access_token, "seller_id":app_info.seller_id, "is_change_project_code":is_change_project_code}
            return invoke_result_data

        # if ":" in user_nick:
        #     invoke_result_data.success = False
        #     invoke_result_data.error_code = "account_error"
        #     invoke_result_data.error_message = "对不起，初次创建活动包含实例化，请使用主账号进行创建。"
        #     return invoke_result_data

        # invoke_result_data = self.get_goods_list(0, 1, "", "", "", access_token, app_key, app_secret)
        # if invoke_result_data.success == False:
        #     invoke_result_data.error_code = "account_error"
        #     invoke_result_data.error_message = "对不起，请使用主账号或者授权的子账号进行创建"
        #     return invoke_result_data

        invoke_result_data = self.get_shop(access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            if invoke_result_data.error_code == "no_power":
                invoke_result_data.error_code = "account_error"
                invoke_result_data.error_message = "该账号无操作权限，请联系主账号开通小程序权限"
            return invoke_result_data

        shop_info = invoke_result_data.data if invoke_result_data.success == True else {}

        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateInstantiateRequest()
            req.clients = share_config.get_value("instantiate_clients","taobao,tmall")
            req.description = description
            req.ext_json = "{ \"name\":\"" + app_name + "\"}"
            req.icon = icon
            req.alias = app_name
            req.template_id = template_id
            req.template_version = template_version
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【小程序实例化】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)

            #录入数据库
            result_app = resp["miniapp_template_instantiate_response"]
            app_info = AppInfo()
            app_info.clients = req.clients
            app_info.app_desc = result_app["app_description"]
            app_info.app_icon = result_app["app_icon"]
            app_info.app_id = result_app["app_id"]
            app_info.app_name = result_app["app_name"]
            app_info.app_ver = result_app["app_version"]
            app_info.app_key = result_app["appkey"]
            app_info.preview_url = result_app["pre_view_url"]
            app_info.template_id = req.template_id
            app_info.template_ver = req.template_version
            app_info.access_token = access_token
            app_info.expiration_date = dead_date
            app_info.project_code = project_code
            app_info.main_user_open_id = main_user_open_id

            if "shop_seller_get_response" in shop_info.keys():
                app_info.store_name = shop_info["shop_seller_get_response"]["shop"]["title"]
                app_info.store_id = shop_info["shop_seller_get_response"]["shop"]["sid"]
                app_info.store_icon = shop_info["shop_seller_get_response"]["shop"]["pic_path"]

            invoke_result_data = self.get_user_seller(access_token,app_key,app_secret, is_log)
            user_seller = invoke_result_data.data if invoke_result_data.success == True else {}
            if "user_seller_get_response" in user_seller.keys():
                app_info.seller_id = user_seller["user_seller_get_response"]["user"]["user_id"]

            app_info.is_instance = is_instance
            app_info.store_user_nick = store_user_nick
            app_info.instance_date = SevenHelper.get_now_datetime()
            app_info.modify_date = SevenHelper.get_now_datetime()
            #上线
            invoke_result_data = self.online_app(app_info.app_id, template_id, template_version, app_info.app_ver, access_token, app_key, app_secret, is_log)
            if invoke_result_data.success == False:
                return invoke_result_data
            online_app_info = invoke_result_data.data
            if "miniapp_template_onlineapp_response" in online_app_info.keys():
                app_info.app_url = online_app_info["miniapp_template_onlineapp_response"]["app_info"]["online_url"]
            app_info.id = app_info_model.add_entity(app_info)
            invoke_result_data.data = {"app_id": app_info.app_id, "store_user_nick": store_user_nick, "user_nick": user_nick, "access_token": access_token, "seller_id":app_info.seller_id, "is_change_project_code":is_change_project_code, "is_first_instance": True}
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=" in content:
                        invoke_result_data.success = False
                        invoke_result_data.error_code = "create_error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        invoke_result_data.data = {"icon": icon, "app_name": app_name}
                        return invoke_result_data

    def version_upgrade(self, app_id, client_template_id, client_ver, access_token, app_key, app_secret, app_info, is_log=False):
        """
        :description: app更新 接口权限包：商家应用-模板实例化权限包
        :param app_id:app_id
        :param client_template_id:模板id
        :param client_ver:更新的版本号
        :param access_token:access_token
        :param app_info:app_info
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateUpdateappRequest()

            req.clients = share_config.get_value("instantiate_clients","taobao,tmall")
            req.app_id = app_id
            req.template_id = client_template_id
            req.template_version = client_ver
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token  + "【app更新】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if resp and ("miniapp_template_updateapp_response" in resp.keys()):
                app_version = resp["miniapp_template_updateapp_response"]["app_version"]
                invoke_result_data = self.online_app(app_id, client_template_id, client_ver, app_version, access_token, app_key, app_secret, is_log)
                online_app_info = invoke_result_data.data if invoke_result_data.success == True else {}
                if "miniapp_template_onlineapp_response" in online_app_info.keys():
                    app_info.app_ver = resp["miniapp_template_updateapp_response"]["app_version"]
                    app_info.template_ver = client_ver
                    app_info.modify_date = SevenHelper.get_now_datetime()
                    AppInfoModel(context=self.context).update_entity(app_info, "app_ver,template_ver,modify_date")
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_sku_name(self, num_iids, sku_id, access_token, app_key, app_secret,is_log=False):
        """
        :description: 获取sku名称
        :param num_iids：num_iids
        :param sku_id：sku_id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = ""
        if not num_iids or not sku_id:
            return invoke_result_data
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsSellerListGetRequest()
            req.fields = "num_iid,title,nick,input_str,property_alias,sku,props_name,pic_url"
            req.num_iids = num_iids
            resp = req.getResponse(access_token)
            if is_log:
                log_info = str(resp) + "【access_token】：" + access_token + "【获取sku名称】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "items_seller_list_get_response" in resp.keys():
                if "items" in resp["items_seller_list_get_response"].keys():
                    props_names = resp["items_seller_list_get_response"]["items"]["item"][0]["props_name"].split(';')
                    if "skus" in resp["items_seller_list_get_response"]["items"]["item"][0]:
                        for sku in resp["items_seller_list_get_response"]["items"]["item"][0]["skus"]["sku"]:
                            if sku["sku_id"] == sku_id:
                                props_name = [i for i in props_names if sku["properties"] in i]
                                if len(props_name) > 0:
                                    invoke_result_data.data = props_name[0][(len(sku["properties"]) + 1):]
                                else:
                                    invoke_result_data.data = sku["properties_name"].split(':')[1]
                                return invoke_result_data
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_buy_order_info(self, order_no, access_token, app_key, app_secret,is_log=False, fields="tid,status,payment,price,created,orders,num,pay_time,buyer_open_uid"):
        """
        :description: 获取单笔订单
        :param order_no：订单编号
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :param fields: 查询字段
        :return: InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpenTradeGetRequest()

            req.fields = fields
            req.tid = order_no
            resp = req.getResponse(access_token)
            if is_log:
                log_info = str(resp) + "【access_token】：" + access_token + "【获取单笔订单】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "open_trade_get_response" in resp.keys():
                if "trade" in resp["open_trade_get_response"]:
                    invoke_result_data.data = resp["open_trade_get_response"]["trade"]
                    return invoke_result_data
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_buy_order_list(self, open_id, access_token, app_key, app_secret, start_created="", end_created="", page_size=50, is_log=False, type="fixed,step",field="tid,status,payment,price,created,orders,num,pay_time,step_trade_status,step_paid_fee,type,outer_iid", page_count = None):
        """
        :description: 获取淘宝购买订单，出现API字段映射错误，请提供参数信息联系小二处理。字段名:buyer_nick，说明open_id跟app_key没对应上，不是app_key下产品的open_id
        :param open_id：open_id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param start_created：开始时间
        :param end_created：结束时间
        :param page_size：页大小
        :param is_log：是否记录返回信息
        :param type：订单类型
        :param field：返回字段
        :param page_count：循坏获取的页数
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        all_order = []
        has_next = True
        if page_size > 100:
            page_size = 100
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpenTradesSoldGetRequest()
            req.fields = field
            req.type = type
            req.buyer_open_id = open_id
            req.page_size = page_size
            req.page_no = 1
            req.use_has_next = "true"

            if start_created == "":
                start_timestamp = TimeHelper.get_now_timestamp() - 90 * 24 * 60 * 60
                start_created = TimeHelper.timestamp_to_format_time(start_timestamp)
            req.start_created = start_created
            if end_created != "":
                req.end_created = end_created

            while has_next:
                resp = req.getResponse(access_token)
                if is_log:
                    log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取购买订单】"
                    if self.context:
                        self.context.logging_link_info(log_info)
                    elif self.logging_link_info:
                        self.logging_link_info(log_info)
                if "open_trades_sold_get_response" in resp.keys():
                    if "trades" in resp["open_trades_sold_get_response"].keys():
                        all_order = all_order + resp["open_trades_sold_get_response"]["trades"]["trade"]
                    req.page_no += 1
                    has_next = resp["open_trades_sold_get_response"]["has_next"]
                    if page_count and req.page_no > page_count:
                        has_next = False
            invoke_result_data.data = all_order
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.data = []
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_refund_order_list(self, open_id, access_token, app_key, app_secret, start_modified="", end_modified="", page_size=50, is_log=False):
        """
        :description: 获取淘宝退款订单
        :param open_id：open_id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param start_modified：开始时间
        :param end_modified：结束时间
        :param page_size：页大小
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        all_order = []
        has_next = True
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.RefundsReceiveGetRequest()
            req.fields = "refund_id,tid,oid,title,total_fee,status,created,refund_fee,modified,num"
            # refund_id：退款单号, tid：淘宝交易单号, oid：子订单号, title：商品名称 , total_fee：订单总价, status：退款状态,
            # created：退款申请时间, refund_fee：退款金额, modified：更新时间, num: 购买数量
            req.type = "fixed"
            req.page_size = page_size
            req.page_no = 1
            req.use_has_next = "true"
            if open_id:
                req.buyer_open_uid = open_id
            if start_modified == "":
                start_timestamp = TimeHelper.get_now_timestamp() - 90 * 24 * 60 * 60
                start_modified = TimeHelper.timestamp_to_format_time(start_timestamp)
            req.start_modified = start_modified
            if end_modified != "":
                req.end_modified = end_modified
            while has_next:
                resp = req.getResponse(access_token)
                if is_log:
                    log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取退单订单】"
                    if self.context:
                        self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
                if "refunds_receive_get_response" in resp.keys():
                    if "refunds" in resp["refunds_receive_get_response"].keys():
                        all_order = all_order + resp["refunds_receive_get_response"]["refunds"]["refund"]
                    req.page_no += 1
                    has_next = resp["refunds_receive_get_response"]["has_next"]
            invoke_result_data.data = all_order
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.data = []
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def online_app(self, app_id, template_id, template_version, app_version, access_token, app_key, app_secret, is_log=False):
        """
        :description: app上线
        :param app_id：app_id
        :param template_id：模板id
        :param template_version：模板版本
        :param app_version：app版本
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateOnlineappRequest()

            req.clients = share_config.get_value("instantiate_clients","taobao,tmall")
            req.app_id = app_id
            req.template_id = template_id
            req.template_version = template_version
            req.app_version = app_version
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【app上线】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_shop(self, access_token, app_key, app_secret, is_log=False):
        """
        :description: 获取店铺信息
        :param access_token：access_token
        :param app_key：app_key
        :param app_secret：app_secret
        :param is_log：是否记录返回信息
        :return: InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ShopSellerGetRequest()
            req.fields = "sid,title,pic_path"
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取店铺信息】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_user_seller(self, access_token, app_key, app_secret, is_log=False):
        """
        :description: 查询卖家用户信息
        :param access_token：access_token
        :param app_key：app_key
        :param app_secret：app_secret
        :param is_log：是否记录返回信息
        :return: InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.UserSellerGetRequest()
            req.fields = "user_id,nick,sex"
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【查询卖家用户信息】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_dead_date(self, user_nick, access_token, app_key, app_secret, is_log=False):
        """
        :description: 获取订购过期时间
        :param user_nick：用户昵称
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            vas_subscribe_get_response = self.get_vas_subscribe(user_nick, access_token, app_key, app_secret, is_log)
            if not vas_subscribe_get_response:
                invoke_result_data.data = "expire"
                return invoke_result_data
            if "article_user_subscribe" not in vas_subscribe_get_response["article_user_subscribes"].keys():
                invoke_result_data.data = "expire"
                return invoke_result_data
            invoke_result_data.data = vas_subscribe_get_response["article_user_subscribes"]["article_user_subscribe"][0]["deadline"]
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_goods_list_by_goodsids(self, num_iids, access_token,app_key, app_secret, field="num_iid,title,nick,pic_url,price,input_str,property_alias,sku,props_name,outer_id,prop_img",is_log=False):
        """
        :description: 获取在售商品列表(num_iids上限20个，超过淘宝会报错)
        :param num_iids：商品id列表
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param field：返回字段
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        num_iid_list = num_iids.split(',')
        page_size = 20
        page_count = int(len(num_iid_list) / page_size) if len(num_iid_list) % page_size == 0 else int(len(num_iid_list) / page_size) + 1
        goods_list = []
        for i in range(0, page_count):
            cur_num_iids = ",".join(num_iid_list[i * page_size:page_size * (i + 1)])
            try:
                top.setDefaultAppInfo(app_key, app_secret)
                req = top.api.ItemsSellerListGetRequest()
                req.fields = field
                req.num_iids = cur_num_iids
                resp = req.getResponse(access_token)
                if is_log:
                    log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取在售商品列表by_goodsids】"
                    if self.context:
                        self.context.logging_link_info(log_info)
                    elif self.logging_link_info:
                        self.logging_link_info(log_info)

                if "items_seller_list_get_response" in resp.keys():
                    if "items" in resp["items_seller_list_get_response"].keys():
                        if "item" in resp["items_seller_list_get_response"]["items"].keys():
                            goods_list.extend(resp["items_seller_list_get_response"]["items"]["item"])
            except Exception as ex:
                if self.context:
                    self.context.logging_link_error(traceback.format_exc())
                elif self.logging_link_error:
                    self.logging_link_error(traceback.format_exc())
                invoke_result_data.success = False
                if "submsg" in str(ex):
                    content_list = str(ex).split()
                    for content in content_list:
                        if "submsg=该子帐号无此操作权限" in content:
                            invoke_result_data.error_code = "no_power"
                            invoke_result_data.error_message = content[len("submsg="):]
                            return invoke_result_data
                        if "submsg=num_iid有误，必须大于0" in content:
                            invoke_result_data.error_code = "param_error"
                            invoke_result_data.error_message = content[len("submsg="):]
                            return invoke_result_data
                        if "submsg=" in content:
                            invoke_result_data.error_code = "error"
                            invoke_result_data.error_message = content[len("submsg="):]
                            return invoke_result_data
                return invoke_result_data
        invoke_result_data.data = {"items_seller_list_get_response": {"items": {"item": goods_list}}}
        return invoke_result_data

    def get_goods_list(self, page_index, page_size, goods_name, order_tag, order_by, access_token,app_key, app_secret, field="num_iid,title,nick,price,input_str,property_alias,sku,props_name,pic_url", is_log=False):
        """
        :description: 获取在售商品列表（获取当前会话用户出售中的商品列表）
        :param page_index：页索引
        :param page_size：页大小
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param field:查询字段
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()

        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsOnsaleGetRequest()
            req.fields = field
            req.page_no = page_index + 1
            req.page_size = page_size
            if goods_name != "":
                req.q = goods_name
            if order_tag !="" and order_by !="":
                req.order_by = order_tag + ":" + order_by
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取在售商品列表】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if resp:
                resp["pageSize"] = page_size
                resp["pageIndex"] = page_index
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_goods_info(self, num_iid, access_token,app_key, app_secret, field="num_iid,title,nick,pic_url,price,item_img.url,outer_id,sku,approve_status,prop_img", is_log=False):
        """
        :description: 获取单个商品详细信息
        :param num_iid：num_iid
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param field：查询字段
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemSellerGetRequest()

            req.fields = field
            req.num_iid = num_iid
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取单个商品详细信息】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_goods_inventory_list(self, page_index, page_size, goods_name, order_tag, order_by, access_token,app_key, app_secret, field="num_iid,title,nick,price,input_str,property_alias,sku,props_name,pic_url", is_log=False):
        """
        :description: 获取仓库商品列表（获取当前用户作为卖家的仓库中的商品列表）
        :param page_index：页索引
        :param page_size：页大小
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param field：查询字段
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsInventoryGetRequest()

            req.fields = field
            req.page_no = page_index
            req.page_size = page_size
            if goods_name != "":
                req.q = goods_name
            req.order_by = order_tag + ":" + order_by

            resp = req.getResponse(access_token)
            if resp:
                resp["pageSize"] = page_size
                resp["pageIndex"] = page_index
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取仓库商品列表】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def miniapp_distribution_items_bind(self, goods_ids, url, status, access_token, app_key, app_secret, is_log=False):
        """
        :description: 小程序投放-商品绑定/解绑（提供给使用了投放插件的服务商，可以调用该API实现帮助商家更新已创建的投放单中的绑定商品信息。）
        :param goods_ids：商品id列表逗号，分隔
        :param url：投放的商家应用完整链接
        :param status：true表示新增绑定，false表示解绑
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappDistributionItemsBindRequest()

            req.target_entity_list = goods_ids
            req.url = url
            req.add_bind = status
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【小程序投放商品】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def miniapp_distribution_order_get(self, order_id_list, access_token, app_key, app_secret, is_log=False):
        """
        :description: 小程序投放-查询小程序投放计划信息
        :param order_id_list:投放计划的id列表 示例值：[1,2,3]
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappDistributionOrderGetRequest()
            req.order_id_request = {}
            req.order_id_request["order_id_list"] = order_id_list
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【查询小程序投放计划】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data

        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def alibaba_benefit_query(self, right_ename, access_token, app_key, app_secret, is_log=False):
        """
        :description: 查询优惠券详情信息
        :param right_ename:奖池ID
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return: InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.AlibabaBenefitQueryRequest()
            req.ename = right_ename
            req.app_name = "promotioncenter-" + share_config.get_value("server_template_id")
            req.award_type = "1"
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【查询优惠券详情信息】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def alibaba_benefit_send(self, right_ename, open_id, access_token,app_key, app_secret, is_log=False):
        """
        :description: 发放优惠劵
        :param right_ename:奖池ID
        :param open_id:open_id
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return: InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.AlibabaBenefitSendRequest()
            req.right_ename = right_ename
            req.receiver_id = open_id
            req.user_type = "taobao"
            req.unique_id = str(open_id) + str(right_ename) + str(TimeHelper.get_now_timestamp())
            req.app_name = "promotioncenter-" + share_config.get_value("server_template_id")
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【发放优惠劵】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_member_info(self, mix_nick, nick, access_token, app_key, app_secret, is_log=False):
        """
        :description: 获取淘宝会员信息
        :param mix_nick:mix_nick
        :param nick:nick（淘宝废弃使用）
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return:InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmMemberIdentityGetRequest()
            if mix_nick:
                req.mix_nick = mix_nick
            if nick:
                req.nick = nick
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取淘宝会员信息】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def check_is_member(self, mix_nick, nick, access_token, app_key, app_secret, is_log=False):
        """
        :description: 实时查询当前是否店铺会员
        :param mix_nick:mix_nick
        :param nick:nick（淘宝废弃使用）
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return:True是会员 False不是会员
        :last_editors: HuangJianYi
        """
        is_member = False
        invoke_result_data = self.get_member_info(mix_nick, nick, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return is_member
        resp = invoke_result_data.data
        if "crm_member_identity_get_response" in resp.keys():
            if "result" in resp["crm_member_identity_get_response"].keys():
                if "member_info" in resp["crm_member_identity_get_response"]["result"].keys():
                    is_member = True
        return is_member

    def get_member_grade(self, mix_nick, access_token, app_key, app_secret, is_log=False):
        """
        :description: 查询会员等级
        :param mix_nick:mix_nick
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return:会员信息
        :last_editors: HuangJianYi
        """
        member_info = {}
        invoke_result_data = self.get_member_info(mix_nick,'', access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return invoke_result_data
        resp = invoke_result_data.data
        if "crm_member_identity_get_response" in resp.keys():
            if "result" in resp["crm_member_identity_get_response"].keys():
                if "member_info" in resp["crm_member_identity_get_response"]["result"].keys():
                    if "grade" in resp["crm_member_identity_get_response"]["result"]["member_info"].keys() and "grade_name" in resp["crm_member_identity_get_response"]["result"]["member_info"].keys():
                        member_info = resp["crm_member_identity_get_response"]["result"]["member_info"]

        invoke_result_data.data = member_info
        return invoke_result_data

    def get_join_member_url(self, access_token, app_key, app_secret, is_log=False):
        """
        :description: 获取加入会员地址
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return:InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmMemberJoinurlGetRequest()
            req.callback_url = ""
            req.extra_info = "{\"source\":\"isvapp\",\"activityId\":\"\",\"entrance\":\"hudong\"}"
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取加入会员地址】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "crm_member_joinurl_get_response" in resp.keys():
                if "result" in resp["crm_member_joinurl_get_response"].keys():
                    if "result" in resp["crm_member_joinurl_get_response"]["result"].keys():
                        invoke_result_data.data = resp["crm_member_joinurl_get_response"]["result"]["result"]
                        if invoke_result_data.data and "https:" not in invoke_result_data.data and "http:" not in invoke_result_data.data:
                            invoke_result_data.data = "https:" + invoke_result_data.data
                        return invoke_result_data
            else:
                invoke_result_data.data = ""
                return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def open_trade_special_items_query(self, app_id, access_token, app_key, app_secret, is_log=False):
        """
        :description: 专属下单查询
        :param app_id：app_id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        resp = {}
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpentradeSpecialItemsQueryRequest()
            req.miniapp_id = app_id
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【专属下单查询】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            invoke_result_data.data = resp
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def open_trade_special_userk_mark(self, goods_id, open_id, access_token, app_key, app_secret, is_log=False):
        """
        :description: 专属下单可购买用户标记
        :param goods_id：商品id
        :param open_id：open_id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpentradeSpecialUsersMarkRequest()
            req.hit = "true"
            req.open_user_ids = str(open_id)
            req.item_id = int(goods_id)
            req.sku_id = 0
            req.status = "MARK"
            req.limit_num = 1
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【专属下单可购买用户标记】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if resp and resp["opentrade_special_users_mark_response"]["result"] == 1:
                #  ------------ TopOpentradeSpecialUserMark: {'opentrade_special_users_mark_response': {'result': 1, 'request_id': 'rsk23xhlk310'}}
                invoke_result_data.data = True
            else:
                invoke_result_data.data = False
            return invoke_result_data

        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def open_trade_special_items_bind(self, app_id, goods_id, access_token, app_key, app_secret, is_log=False):
        """
        :description: 专属下单商品绑定
        :param app_id：app_id
        :param goods_id：goods_id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpentradeSpecialItemsBindRequest()

            req.miniapp_id = app_id
            req.item_ids = str(goods_id)
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【专属下单商品绑定】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            # {'opentrade_special_items_bind_response': {'results': {'item_bind_result': [{'bind_ok': False, 'error_message': '商品已绑定到小程序:情之缘1993_好货跳一跳_[3000000029278805]', 'item_id': 632007280726}]}, 'request_id': 'zrq8mt8d8xdo'}}
            if resp["opentrade_special_items_bind_response"]["results"]["item_bind_result"][0]:
                if not resp["opentrade_special_items_bind_response"]["results"]["item_bind_result"][0]["bind_ok"]:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = resp["opentrade_special_items_bind_response"]["results"]["item_bind_result"][0]["error_message"]
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_project_code(self, user_nick, access_token, app_key, app_secret, is_log=False):
        """
        :description: 获取项目编码
        :param user_nick：用户昵称
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return list
        :last_editors: HuangJianYi
        """
        try:
            vas_subscribe_get_response = self.get_vas_subscribe(user_nick, access_token, app_key, app_secret, is_log)
            if not vas_subscribe_get_response:
                return ""
            if "article_user_subscribe" not in vas_subscribe_get_response["article_user_subscribes"].keys():
                return ""
            return vas_subscribe_get_response["article_user_subscribes"]["article_user_subscribe"][0]["item_code"]
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            return ""

    def get_vas_subscribe(self, user_nick, access_token, app_key, app_secret, is_log=False):
        """
        :description:订购关系查询 用于ISV根据登录进来的淘宝会员名查询该为该会员开通哪些收费项目，ISV只能查询自己名下的应用及收费项目的订购情况
        :param user_nick：用户昵称
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 订购关系
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            cache_key = f"get_vas_subscribe:{user_nick}"
            vas_subscribe_get_response = redis_init.get(cache_key)
            if vas_subscribe_get_response:
                return json.loads(vas_subscribe_get_response)
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.VasSubscribeGetRequest()
            req.article_code = share_config.get_value("article_code")
            req.nick = user_nick
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【订购关系查询】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            redis_init.set(cache_key, json.dumps(resp["vas_subscribe_get_response"]),5)
            return resp["vas_subscribe_get_response"]
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            return None

    def get_short_url(self, url, access_token, app_key, app_secret, is_log=False):
        """
        :description: 获取短链接（提供淘宝小程序短链接生成的能力，只允许对淘宝小程序对应的域名：https://m.duanqu.com/ 生成对应的短链接，其他域名无效 【特别注意：短链接有效期为30天，超过时效短链接将无法正常跳转到原始链接地址，请勿将短链接投放或装修到长期存在的入口】）
        :param url：链接地址
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 短链接地址
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappShorturlCreateRequest()
            req.article_code = share_config.get_value("article_code")
            req.miniapp_url = url
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取短链接】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "miniapp_shorturl_create_response" not in  resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["miniapp_shorturl_create_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            if "model" not in resp["miniapp_shorturl_create_response"]["result"]:
                invoke_result_data.success = False
                return invoke_result_data
            if "short_url" not in resp["miniapp_shorturl_create_response"]["result"]["model"]:
                invoke_result_data.success = False
                return invoke_result_data
            invoke_result_data.data = resp["miniapp_shorturl_create_response"]["result"]["model"]["short_url"]
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            return invoke_result_data

    def get_crm_point_available(self, mix_nick, access_token, app_key, app_secret, is_log=False, open_id=""):
        """
        :description: 获取店铺会员积分
        :param mix_nick：混淆昵称
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :param open_id：open_id
        :return 返回店铺会员积分
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmPointAvailableGetRequest()
            if mix_nick:
                req.mix_nick = mix_nick
            if open_id:
                req.open_uid = open_id
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【获取店铺会员积分】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "crm_point_available_get_response" not in  resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["crm_point_available_get_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            invoke_result_data.data = resp["crm_point_available_get_response"]["result"]
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def change_crm_point(self, open_id, mix_nick, change_type, opt_type, quantity, access_token, app_key, app_secret, activity_id=0, activity_name="", is_log=False, account_date=""):
        """
        :description: 操作店铺会员积分
        :param open_id：买家open_id
        :param mix_nick：混淆昵称
        :param change_type：变更类型：0交易，1：互动活动，2：权益兑换，3：手工调整
        :param opt_type：操作类型，0：增加，1：扣减
        :param quantity：积分数量
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param activity_id：活动Id
        :param activity_name：活动名称
        :param is_log：是否记录返回信息
        :param account_date：积分有效期，主要用于互动场景,示例值：2017-07-30
        :return 返回操作结果
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmPointChangeRequest()
            if activity_id > 0:
                req.activity_id = activity_id
            if activity_name:
                req.activity_name = activity_name
            if account_date:
                req.account_date = account_date
            else:
                crm_point_account_date = share_config.get_value("crm_point_account_date", 0)
                if crm_point_account_date > 0:
                    req.account_date = TimeHelper.add_days_by_format_time(day=crm_point_account_date, format='%Y-%m-%d')
            req.change_type = change_type
            req.opt_type = opt_type
            req.quantity = quantity
            if open_id:
                req.open_id = open_id
            if mix_nick:
                req.mix_nick = mix_nick
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【操作店铺会员积分】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "crm_point_change_response" not in resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["crm_point_change_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            invoke_result_data.data = resp["crm_point_change_response"]["result"]
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def miniapp_widget_template_instance_query(self, widget_template_id, access_token, app_key, app_secret, is_log=False):
        """
        :description: 查询淘宝小部件信息
        :param widget_template_id：小部件模版id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 小部件实例化信息
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappWidgetTemplateInstanceQueryRequest()
            req.param0 = {}
            req.param0["page_size"] = 20
            req.param0["page_num"] = 1
            req.param0["template_id"] = widget_template_id
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【查询淘宝小部件信息】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            return invoke_result_data

        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def miniapp_widget_template_instantiate(self, template_version, description, widget_template_id, access_token, app_key, app_secret, is_log=False):
        """
        :description: 实例化小部件 resp={"miniapp_widget_template_instantiate_response": {"result": {"model": {"app_description": "提供商家会员权益集合", "app_icon": "https://ossgw.alicdn.com/taobao-miniapp/img/39eb12a3c266c7a8d72e8dcb1b6a1530.png", "app_name": "天志C店_会员身份卡片", "appkey": "400013325276", "id": "3000000070599924", "online_code": "https://m.duanqu.com/?_ariver_appid=3000000070599924&_mp_code=tb&transition=present", "online_version": "0.0.1"}, "success": True}, "request_id": "15rv0rkcwiqtn"}}
        :param template_version：小部件版本
        :param description：小部件描述
        :param widget_template_id：小部件模版id
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 实例化后的信息
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappWidgetTemplateInstantiateRequest()
            req.param_mini_app_instantiate_template_app_simple_request = {}
            req.param_mini_app_instantiate_template_app_simple_request["template_id"] = widget_template_id
            req.param_mini_app_instantiate_template_app_simple_request["template_version"] = template_version
            req.param_mini_app_instantiate_template_app_simple_request["description"] = description
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【实例化小部件】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "miniapp_widget_template_instantiate_response" not in resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["miniapp_widget_template_instantiate_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            if resp["miniapp_widget_template_instantiate_response"]["result"]["success"] == False:
                invoke_result_data.success = False
                return invoke_result_data

            invoke_result_data.data = resp["miniapp_widget_template_instantiate_response"]["result"]["model"]
            return invoke_result_data

        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def miniapp_widget_template_instance_update(self, widgets_id, widget_template_id, template_version, access_token, app_key, app_secret, is_log=False):
        """
        :description: 更新小部件版本
        :param widgets_id：小部件id
        :param widget_template_id：小部件模版id
        :param template_version：小部件模版版本
        :param access_token：access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappWidgetTemplateInstanceUpdateRequest()
            req.param_mini_app_instantiate_template_app_update_request = {}
            req.param_mini_app_instantiate_template_app_update_request["entity_id"] = widgets_id
            req.param_mini_app_instantiate_template_app_update_request["template_id"] = widget_template_id
            req.param_mini_app_instantiate_template_app_update_request["template_version"] = template_version
            resp = req.getResponse(access_token)
            if is_log:
                log_info = "【req】:" + SevenHelper.json_dumps(req) + "【resp】:" + SevenHelper.json_dumps(resp) + "【access_token】：" + access_token + "【更新小部件版本】"
                if self.context:
                    self.context.logging_link_info(log_info)
                elif self.logging_link_info:
                    self.logging_link_info(log_info)
            if "miniapp_widget_template_instance_update_response" not in resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["miniapp_widget_template_instance_update_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            if resp["miniapp_widget_template_instance_update_response"]["result"]["success"] == False:
                invoke_result_data.success = False
                return invoke_result_data
            invoke_result_data.data = resp["miniapp_widget_template_instance_update_response"]["result"]["model"]
            return invoke_result_data

        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data