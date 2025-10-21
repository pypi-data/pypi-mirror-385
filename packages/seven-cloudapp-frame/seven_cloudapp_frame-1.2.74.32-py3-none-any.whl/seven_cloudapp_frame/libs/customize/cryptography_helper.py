# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-10-08 22:01:47
@LastEditTime: 2023-04-19 15:55:32
@LastEditors: HuangJianYi
@Description: 
"""
from Crypto.Cipher import AES
import base64
import re
from emoji import unicode_codes
import hashlib
from seven_framework import *

class CryptographyHelper:
    """
    :description: 加密帮助类
    :return: 
    :last_editors: HuangJianYi
    """

    @classmethod
    def emoji_base64_to_emoji(self, text_str):
        """
        :description: 把加密后的表情还原
        :param text_str: 加密后的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        results = re.findall('\[em_(.*?)\]', str(text_str))
        if results:
            for item in results:
                text_str = str(text_str).replace("[em_{0}]".format(item), self.base64_decrypt(item))
        return text_str

    @classmethod
    def emoji_to_emoji_base64(self, text_str):
        """
        :description: emoji表情转为[em_xxx]形式存于数据库,打包每一个emoji
        :description: 性能遇到问题时重新设计转换程序
        :param text_str: 未加密的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        list_e = []
        for i in text_str:
            list_e.append(i)
        for location, item_emoji in enumerate(text_str):
            if item_emoji in unicode_codes.UNICODE_EMOJI["en"]:
                emoji_base64 = self.base64_encrypt(item_emoji, "utf-8")
                list_e[location] = "[em_" + emoji_base64 + "]"
        return "".join(list_e)

    @classmethod
    def base64_encrypt(self, source, encoding="utf-8"):
        """
        :Description: base64加密
        :param source: 需加密的字符串
        :return: 加密后的字符串
        :last_editors: HuangJianYi
        """
        if not source.strip():
            return ""
        cipher_text = str(base64.b64encode(source.encode(encoding=encoding)), 'utf-8')
        return cipher_text

    @classmethod
    def base64_decrypt(self, source):
        """
        :Description: base64解密
        :param source: 需加密的字符串
        :return: 解密后的字符串
        :last_editors: HuangJianYi
        """
        if not source.strip():
            return ""
        plain_text = str(base64.b64decode(source), 'utf-8')
        return plain_text

    @classmethod
    def aes_encrypt(self, source, password, iv, mode=AES.MODE_CBC, pad_char='\0', encoding="utf-8"):
        """
        :Description: AES加密,默认CBC & ZeroPadding
        :param source: 待加密字符串
        :param password: 密钥
        :param iv: 偏移量
        :param mode: AES加密模式
        :param pad_char: 填充字符
        :param encoding: 编码
        :return: 加密后的字符串
        :last_editors: HuangJianYi
        """
        source = source.encode(encoding)
        password = password.encode(encoding)
        iv = iv.encode(encoding)
        cryptor = AES.new(password, mode, iv)
        # 这里密钥password 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        length = 16
        count = len(source)
        if count > 0:
            if count < length:
                add = (length - count)
                source = source + (pad_char * add).encode(encoding)
            elif count > length:
                add = (length - (count % length))
                source = source + (pad_char * add).encode(encoding)
        cipher_text = cryptor.encrypt(source)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为base64
        return str(base64.b64encode(cipher_text), encoding)

    @classmethod
    def aes_decrypt(self, source, password, iv, mode=AES.MODE_CBC, encoding="utf-8"):
        """
        :Description: AES解密,默认CBC
        :param source: 待解密字符串
        :param password: 密钥
        :param iv: 偏移量
        :param mode: AES加密模式
        :param encoding: 编码
        :return: 解密后的明文
        :last_editors: HuangJianYi
        """
        try:
            encry_text = base64.b64decode(source)
            password = password.encode(encoding)
            iv = iv.encode(encoding)
            cryptor = AES.new(password, mode, iv)
            plain_text = cryptor.decrypt(encry_text)
            plain_text = str(plain_text, encoding)
            index = plain_text.rindex('}') + 1
            return plain_text[0:index]
        except Exception as ex:
            return ""

    @classmethod
    def signature_md5(self, request_param_dict, encrypt_key=""):
        """
        :description: 参数按照加密规则进行MD5加密
        :description: 签名规则 signature_md5= ((参数1=参数1值&参数2=参数2值&signature_stamp={signature_stamp}))+密钥)进行Md5加密转小写，参数顺序按照字母表的顺序排列
        :param request_param_dict: 请求参数字典
        :param encrypt_key: 接口密钥
        :return: 加密后的md5值，由于跟客户端传来的加密参数进行校验
        """
        request_sign_params = {}
        for k, v in request_param_dict.items():
            if k == "param_signature_md5":
                continue
            if k == "signature_md5":
                continue
            request_sign_params[k] = str(v).replace(" ", "_seven_").replace("(", "_seven1_").replace(")", "_seven2_")
        request_params_sorted = sorted(request_sign_params.items(), key=lambda e: e[0], reverse=False)
        request_message = "&".join(k + "=" + CodingHelper.url_encode(v) for k, v in request_params_sorted)
        request_message = request_message.replace("_seven_", "%20").replace("_seven1_", "(").replace("_seven2_", ")").replace("%27", "'")
        # MD5摘要
        request_encrypt = hashlib.md5()
        request_encrypt.update((request_message + str(encrypt_key)).encode("utf-8"))
        check_request_signature_md5 = request_encrypt.hexdigest().lower()
        return check_request_signature_md5