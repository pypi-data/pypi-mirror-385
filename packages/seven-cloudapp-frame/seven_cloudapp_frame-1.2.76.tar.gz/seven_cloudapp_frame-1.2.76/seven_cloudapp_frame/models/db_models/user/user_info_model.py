# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-22 10:59:39
@LastEditTime: 2024-01-03 10:46:40
@LastEditors: HuangJianYi
@Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class UserInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None, is_auto=False):
        super(UserInfoModel, self).__init__(UserInfo, sub_table)
        db_connect_key, self.redis_config_dict = SevenHelper.get_connect_config("db_user","redis_user", db_connect_key)
        self.db = MySQLHelper(self.convert_db_config(db_connect_key, is_auto))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class UserInfo:

    def __init__(self):
        super(UserInfo, self).__init__()
        self.id = 0  # id
        self.id_md5 = ""  # id_md5(act_id+user_id)md5int生成
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.union_id = ""  # union_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 昵称
        self.user_nick_encrypt = ""  # 昵称加密值
        self.avatar = ""  # 头像
        self.is_auth = 0  # 是否授权（1是0否）
        self.is_new = 0  # 是否新用户
        self.pay_price = 0  # 累计支付金额
        self.pay_num = 0  # 累计支付笔数
        self.login_token = ""  # 登录令牌
        self.user_state = 0  # 用户状态（0-正常，1-黑名单）
        self.is_member = 0  # 是否会员
        self.is_member_before = 0  # 用户最初会员状态
        self.is_favor = 0  # 是否关注店铺
        self.is_favor_before = 0  # 用户最初关注状态（0未关注1已关注）
        self.sex = 0  # 性别（0-未知，1-男，2-女）
        self.birthday = "1900-01-01 00:00:00" # 出生日期
        self.telephone = "" # 手机号码
        self.plat_type = 0 # 注册平台类型(查看枚举类)
        self.relieve_date = "1900-01-01 00:00:00"  # 解禁时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.i1 = 0  # i1
        self.i2 = 0  # i2
        self.i3 = 0  # i3
        self.i4 = 0  # i4
        self.i5 = 0  # i5
        self.s1 = ""  # s1
        self.s2 = ""  # s2
        self.s3 = ""  # s3
        self.s4 = ""  # s4
        self.s5 = ""  # s5
        self.d1 = "1900-01-01 00:00:00"  # d1
        self.d2 = "1900-01-01 00:00:00"  # d2

    @classmethod
    def get_field_list(self):
        return ['id', 'id_md5', 'app_id', 'act_id', 'user_id', 'union_id', 'open_id', 'user_nick', 'user_nick_encrypt', 'avatar', 'is_auth', 'is_new', 'pay_price', 'pay_num', 'login_token', 'user_state', 'is_member', 'is_member_before', 'is_favor', 'is_favor_before', 'sex', 'birthday', 'telephone', 'plat_type', 'relieve_date', 'create_date', 'modify_date', 'i1', 'i2', 'i3', 'i4', 'i5', 's1', 's2', 's3', 's4', 's5', 'd1', 'd2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "user_info_tb"
