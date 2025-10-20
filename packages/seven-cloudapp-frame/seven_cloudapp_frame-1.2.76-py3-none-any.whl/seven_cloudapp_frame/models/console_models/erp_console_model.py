# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-11-24 09:36:39
@LastEditTime: 2025-03-10 15:54:03
@LastEditors: HuangJianYi
@Description: ERP控制台业务模型(用于跟遁甲系统对接，推送订单和回写物流) 需在配置文件加 armor_url 和 armor_sign_key对应的值
"""

import threading, multiprocessing
from seven_framework import *
from seven_cloudapp_frame.libs.common.frame_console import *
from seven_cloudapp_frame.libs.common import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.frame_base_model import FrameBaseModel
from seven_cloudapp_frame.models.db_models.erp.erp_relation_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_order_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *


class ErpConsoleModel():
    """
    :description: ERP控制台业务模型(用于跟遁甲系统对接，推送订单和回写物流)
    """
    def __init__(self):
        """
        :description: 初始化
        :return: 
        :last_editors: HuangJianYi
        """
        self.db_connect_key, self.redis_config_dict = SevenHelper.get_connect_config("db_order","redis_order")

    def console_erp(self, mod_count=1, prize_roster_model=None, process_type=1):
        """
        :description: 控制台推送订单和回写物流
        :param mod_count: 单表队列数
        :param prize_roster_model: 中奖记录model实例化
        :param process_type: 处理方式（1.redis 2.api） 如果是淘系使用redis处理方式非淘系用api模式
        :return: 
        :last_editors: HuangJianYi
        """
        for i in range(mod_count):

            t = threading.Thread(target=self.process_order_push, args=[i, mod_count, True, prize_roster_model])
            t.start()

            j = threading.Thread(target=self.process_order_pull, args=[i, mod_count, process_type, prize_roster_model])
            j.start()

    def process_order_push(self, mod_value, mod_count, is_loop=True, prize_roster_model=None, decrypt_field_list=["real_name","telephone","province","city","county","street","address"]):
        """
        :description: 处理订单推送到遁甲系统
        :param mod_value: 当前队列值
        :param mod_count: 队列数
        :param is_loop: 是否循环
        :param prize_roster_model: 中奖记录model实例化
        :param decrypt_field_list: 需要解密的字段列表
        :return: 
        :last_editors: HuangJianYi
        """
        page_size = 100
        push_url = share_config.get_value("armor_url", "") + "/api/new_order"
        sign_key = share_config.get_value("armor_sign_key", "")

        print(f"{TimeHelper.get_now_format_time()} 推送订单队列{mod_value}启动")

        while True:
            try:
                time.sleep(1)
                heart_beat_monitor("process_order_push")
                erp_relation_model = ErpRelationModel()
                frame_base_model = FrameBaseModel()
                now_date = TimeHelper.get_now_format_time()
                if mod_count == 1:
                    erp_relation_list = erp_relation_model.get_dict_list("is_release=1 and %s>sync_date and start_date<=%s and end_date>=%s", order_by="sync_date asc", limit="200", params=[TimeHelper.add_minutes_by_format_time(minute=-10), now_date, now_date])
                else:
                    erp_relation_list = erp_relation_model.get_dict_list("MOD(id,%s)=%s and is_release=1 and %s>sync_date and start_date<=%s and end_date>=%s", order_by="sync_date asc", limit="200", params=[mod_count, mod_value, TimeHelper.add_minutes_by_format_time(minute=-10), now_date, now_date])
                if len(erp_relation_list) > 0:
                    for erp_relation_dict in erp_relation_list:
                        try:
                            erp_relation_model.update_table("sync_date=%s", "id=%s", params=[TimeHelper.get_now_format_time(), erp_relation_dict["id"]])
                            prize_order_model = PrizeOrderModel().set_sub_table(erp_relation_dict["app_id"])
                            if not prize_roster_model:
                                prize_roster_model = PrizeRosterModel().set_sub_table(erp_relation_dict["app_id"])
                            condition = "app_id=%s and order_status=0 and sync_status=0 and create_date<%s"
                            params = [erp_relation_dict["app_id"], TimeHelper.add_minutes_by_format_time(minute=-5)]
                            record_count = prize_order_model.get_total(condition, params=params)
                            page_count = SevenHelper.get_page_count(page_size, record_count)
                            for page_index in range(page_count):
                                prize_order_dict_list = prize_order_model.get_dict_list(condition, "", order_by="id asc", limit=str(page_size), field="*", params=params)
                                for prize_order_dict in prize_order_dict_list:
                                    prize_order_dict, status = frame_base_model.sensitive_decrypt(prize_order_dict, decrypt_field_list)
                                    if status == 0:
                                        prize_order_model.update_table("sync_status=2,sync_date=%s,sync_result=%s", "id=%s", params=[TimeHelper.get_now_format_time(), f"敏感字段解密失败,ex:{traceback.format_exc()}", prize_order_dict["id"]])
                                        continue
                                    request_params = self.compose_push_request_params(sign_key, erp_relation_dict, prize_order_dict, prize_roster_model)
                                    if request_params["goods"]:
                                        result = HTTPHelper.post(push_url, request_params, {"Content-Type": "application/json"})
                                        if result and result.ok:
                                            prize_order_model.update_table("sync_status=1,sync_date=%s", "id=%s", params=[TimeHelper.get_now_format_time(), prize_order_dict["id"]])
                                        else:
                                            prize_order_dict["sync_count"] = prize_order_dict["sync_count"] + 1
                                            if prize_order_dict["sync_count"] == 10:
                                                prize_order_model.update_table("sync_status=2,sync_date=%s,sync_result=%s", "id=%s", params=[TimeHelper.get_now_format_time(), SevenHelper.json_dumps(result), prize_order_dict["id"]])
                                            else:
                                                prize_order_model.update_table("sync_count=sync_count+1,sync_date=%s,sync_result=%s", "id=%s", params=[TimeHelper.get_now_format_time(), SevenHelper.json_dumps(result), prize_order_dict["id"]])
                                    else:
                                        prize_order_model.update_table("sync_status=2,sync_date=%s,sync_result=%s", "id=%s", params=[TimeHelper.get_now_format_time(), "推送订单失败，没有商品信息", prize_order_dict["id"]])

                        except Exception as ex:
                            logger_error.error(f"推送订单队列{mod_value}异常,json串:{SevenHelper.json_dumps(erp_relation_dict)},ex:{traceback.format_exc()}")
                            continue

                if is_loop == True and len(erp_relation_list) <= 0:
                    time.sleep(60)
                if is_loop == False:
                    break
            except Exception as ex:
                time.sleep(5)

    def compose_push_request_params(self, sign_key, erp_relation_dict, prize_order_dict, prize_roster_model):
        """
        :description: 合成请求参数
        :param sign_key: 接口签名key
        :param erp_relation_dict: erp关联信息
        :param prize_order_dict: 订单信息
        :param prize_roster_model: 中奖记录实例
        :return: 
        :last_editors: HuangJianYi
        """
        data = {}
        data["product_id"] = config.get_value("project_name", 0)
        data["business_name"] = erp_relation_dict["store_name"]
        data["app_id"] = erp_relation_dict["app_id"]
        data["app_key"] = erp_relation_dict["app_key"]
        data["mini_order"] = prize_order_dict["order_no"]
        data["user_id"] = prize_order_dict["user_id"]
        data["open_id"] = prize_order_dict["open_id"]
        data["user_account"] = prize_order_dict["user_nick"]
        data["order_time"] = TimeHelper.datetime_to_timestamp(prize_order_dict["create_date"]) * 1000 if str(prize_order_dict["create_date"]) != "1900-01-01 00:00:00" else 0
        data["activity_id"] = prize_order_dict["act_id"]
        data["activity_name"] = ""
        data["order_price"] = str(prize_order_dict['order_price'])
        data["consignee"] = prize_order_dict["real_name"]
        data["phone"] = prize_order_dict["telephone"]
        data["province"] = prize_order_dict["province"]
        data["city"] = prize_order_dict["city"]
        data["county"] = prize_order_dict["county"]
        data["street"] = prize_order_dict["street"]
        data["address"] = prize_order_dict["address"]
        data["remark"] = prize_order_dict["seller_remark"]
        data["buyer_remark"] = prize_order_dict["buyer_remark"]
        data["freight_price"] = str(prize_order_dict["freight_price"])
        data["timestamp"] = TimeHelper.get_now_timestamp(True)
        data["order_status"] = prize_order_dict["order_status"]
        if data["order_status"] == 2:
            data["order_status"] = -1  #遁甲系统 不予发货固定是-1
        if data["order_status"] == 1:
            data["logistics_number"] = prize_order_dict["express_no"]
            data["logistics_company"] = prize_order_dict["express_company"]
            data["delivery_time"] = TimeHelper.datetime_to_timestamp(prize_order_dict["deliver_date"]) * 1000 if str(prize_order_dict["deliver_date"]) != "1900-01-01 00:00:00" else 0

        goods_list = []
        prize_roster_list_dict = prize_roster_model.get_dict_list("order_no=%s", "", "id desc", "", "*", prize_order_dict["order_no"])
        for prize_roster_dict in prize_roster_list_dict:
            goods = {}
            goods["main_order"] = prize_roster_dict["main_pay_order_no"]
            goods["sub_order"] = prize_roster_dict["sub_pay_order_no"]
            goods["goods_name"] = prize_roster_dict["prize_name"]
            goods["goods_price"] = str(prize_roster_dict["prize_price"])
            goods["goods_code"] = prize_roster_dict["goods_code"]
            goods["goods_id"] = prize_roster_dict["goods_id"]
            goods["sku"] = prize_roster_dict["sku_id"]
            goods["goods_count"] = 1
            goods_list.append(goods)
        data["goods"] = goods_list
        data["sign"] = SignHelper.params_sign_md5(data, sign_key)
        return data

    def process_order_pull(self, mod_value, mod_count, process_type=1, prize_roster_model=None):
        """
        :description: 处理订单拉取，同步物流信息
        :param mod_value: 当前队列值
        :param mod_count: 队列数
        :param process_type: 处理方式（1.redis 2.api） 如果是淘系使用redis处理方式非淘系用api模式
        :param prize_roster_model: 中奖记录model实例化
        :return: 
        :last_editors: HuangJianYi
        """
        print(f"{TimeHelper.get_now_format_time()} 拉取订单队列{mod_value}启动")
        #获取产品id
        project_name = config.get_value("project_name", 0)
        while True:
            try:
                time.sleep(1)
                heart_beat_monitor("process_order_pull")
                erp_relation_model = ErpRelationModel()
                erp_redis_init = SevenHelper.redis_init(config_dict=config.get_value("erp_redis"))
                # frame_base_model = FrameBaseModel()
                now_date = TimeHelper.get_now_format_time()
                if mod_count == 1:
                    erp_relation_list = erp_relation_model.get_dict_list("is_release=1 and %s>return_date and start_date<=%s and end_date>=%s", order_by="return_date asc", limit="200", params=[TimeHelper.add_minutes_by_format_time(minute=-10), now_date, now_date])
                else:
                    erp_relation_list = erp_relation_model.get_dict_list("MOD(id,%s)=%s and is_release=1 and %s>return_date and start_date<=%s and end_date>=%s", order_by="return_date asc", limit="200", params=[mod_count, mod_value, TimeHelper.add_minutes_by_format_time(minute=-10), now_date, now_date])
                if len(erp_relation_list) > 0:
                    for erp_relation_dict in erp_relation_list:
                        try:
                            prize_order_model = PrizeOrderModel().set_sub_table(erp_relation_dict["app_id"])
                            if not prize_roster_model:
                                prize_roster_model = PrizeRosterModel().set_sub_table(erp_relation_dict["app_id"])
                            erp_relation_model.update_table("return_date=%s", "id=%s", params=[TimeHelper.get_now_format_time(), erp_relation_dict["id"]])
                            if process_type == 1:
                                key = "order_" + project_name + "_" + erp_relation_dict["app_id"]
                                tatal_count = erp_redis_init.llen(key)
                                if tatal_count <= 0:
                                    #logger_info.info("redis订单数量：" + str(tatal_count) + "，key=" + key)
                                    continue
                                index = 0
                                while True:
                                    order_info_json = erp_redis_init.lindex(key, index=index)
                                    if not order_info_json:
                                        break
                                    order_info_dict = json.loads(order_info_json)
                                    order_status = order_info_dict["order_status"]
                                    order_no = order_info_dict["mini_order"]
                                    express_no = order_info_dict["logistics_number"]
                                    express_company = order_info_dict["logistics_company"]
                                    delivery_time = order_info_dict["delivery_time"]
                                    modify_date = TimeHelper.get_now_datetime()
                                    if order_status == 1:
                                        delivery_time = TimeHelper.timestamp_to_datetime(delivery_time)
                                        update_sql = "order_status=1,express_no=%s,express_company=%s,deliver_date=%s,sync_date=%s"
                                        params = [express_no, express_company, delivery_time, modify_date, order_no]
                                        prize_order_model.update_table(update_sql, "order_no=%s", params=params)
                                        prize_roster_model.update_table("logistics_status=1", "app_id=%s and order_no=%s", params=[erp_relation_dict["app_id"], order_no])
                                        self.process_order_pull_executed(order_info_dict)
                                    else:
                                        update_sql = "sync_status=2,sync_date=%s,sync_result=%s"
                                        params = [modify_date, "拉取订单失败", order_no]
                                        prize_order_model.update_table(update_sql, "order_no=%s", params=params)
                                    #删除redis缓存
                                    erp_redis_init.lpop(key)
                            else:
                                page_size = 100
                                pull_url = share_config.get_value("armor_url","") + "/api/new_get_order"
                                sign_key = share_config.get_value("armor_sign_key", "")
                                condition = "app_id=%s and order_status=0 and sync_status=1"
                                params = [erp_relation_dict["app_id"]]
                                record_count = prize_order_model.get_total(condition, params=params)
                                page_count = SevenHelper.get_page_count(page_size, record_count)
                                for page_index in range(0, page_count):
                                    prize_order_dict_list = prize_order_model.get_dict_page_list("id,order_no", page_index, page_size, condition, "", "id asc", params, page_count_mode="none")
                                    if prize_order_dict_list and len(prize_order_dict_list) > 0:
                                        order_no_list = [prize_order['order_no'] for prize_order in prize_order_dict_list]
                                        data = {}
                                        data["mini_order"] = ",".join(order_no_list)
                                        data["timestamp"] = TimeHelper.get_now_timestamp(True)
                                        data["sign"] = SignHelper.params_sign_md5(data, sign_key)
                                        result = HTTPHelper.post(pull_url, data, {"Content-Type": "application/json"})
                                        if result and result.ok:
                                            result = json.loads(result.text)
                                            data_list = result["data"]
                                            if not data_list:
                                                continue
                                            data_list = [i for i in data_list if i['order_status'] in (1, 2)]
                                            if data_list:
                                                for data in data_list:
                                                    order_status = data["order_status"]
                                                    order_no = data["mini_order"]
                                                    express_no = data["logistics_number"]
                                                    express_company = data["logistics_company"]
                                                    delivery_time = data["delivery_time"]
                                                    modify_date = TimeHelper.get_now_datetime()
                                                    if order_status == 1:
                                                        delivery_time = TimeHelper.timestamp_to_datetime(delivery_time)
                                                        update_sql = "order_status=1,express_no=%s,express_company=%s,deliver_date=%s,sync_date=%s"
                                                        update_params = [express_no, express_company, delivery_time, modify_date, order_no]
                                                        prize_order_model.update_table(update_sql, "order_no=%s", params=update_params)
                                                        prize_roster_model.update_table("logistics_status=1", "app_id=%s and order_no=%s", params=[erp_relation_dict["app_id"], order_no])
                                                        self.process_order_pull_executed(data)
                                                    else:
                                                        update_sql = "sync_status=2,sync_date=%s,sync_result=%s"
                                                        update_params = [modify_date, "拉取订单失败", order_no]
                                                        prize_order_model.update_table(update_sql, "order_no=%s", params=update_params)
                        except Exception as ex:
                            logger_error.error(f"拉取订单队列{mod_value}异常,json串:{SevenHelper.json_dumps(erp_relation_dict)},ex:{traceback.format_exc()}")
                            continue
                else:
                    time.sleep(60)
            except Exception as ex:
                time.sleep(5)

    def process_order_pull_executed(self, order_info_dict):
        """
        :description: 拉取订单执行后事件
        :param order_info_dict: 订单信息字典
        :return: 
        :last_editors: HuangJianYi
        """
