import time
import re
import random
import requests

from requests.cookies import RequestsCookieJar
from common.log.log_manager import logger
from plugin.PixivAide.constants.pixiv_constant import PixivConstant
from fake_useragent import UserAgent


class Client(object):

    def __init__(self, cookies):
        self.headers = None
        # 用户自定义cookie
        self.orig_cookie_list = cookies
        # 生成cookie_list
        self.cookie_list = []
        # 该客户端使用的Cookie
        self.cookie = None
        # 该客户端（随机Cookie）使用的账号ID
        self.user_id = ''
        self.session = requests.session
        self._generate_headers()
        self._orig_cookie_list_to_cookie_jar()

    def _generate_headers(self):
        """
        * 功能描述: 生成请求头
        * @fileName: client.py
        * @Author: Messiah
        * @Date: 2024/11/20
        """
        self.headers = {
            'Referer': PixivConstant.HOST_URL,
            "Accept-Language": "zh-CN,zh;q=0.9",  # 返回translation,中文翻译的标签组
            'User-Agent': UserAgent().random,
            # 'Host': PixivConstants.HOST_URL,
            # "Origin": "https://accounts.pixiv.net",
            # 'Cookie': self.cookie
        }
        logger.debug(f"初始化headers成功:{self.headers}")

    def base_request(self, options, data=None, params=None, retry_num=5):
        """
        * 功能描述:
        * @parm: options: 请求参数,暂时只用到url和headers：options ={"url":"origin_url","headers":demo_headers}
                          优先使用options中的headers,否则使用self.headers（初始化时从配置加载的headers）
        * @parm: data: Post参数
        * @parm: params: Get参数
        * @parm: retry_num: 重试次数
        * @return: response对象/False
        * @fileName: client.py
        * @Author: Messiah
        * @Date: 2024/9/6 13:40
        """

        try:
            response = self.session().get(
                options.get("url"),
                data=data,
                params=params,
                cookies=self.cookie,
                headers=options.get("headers", self.headers),
                verify=False,
                timeout=10,
            )
            if response and response.status_code == 200:  # 进一步检查响应内容
                return response
            else:
                logger.warning(f"无效的响应: {response.status_code if response else '无响应'}")
                return None
        except Exception as e:
            if retry_num > 0:
                logger.warning(f"尝试重新请求:{options["url"]}")
                time.sleep(1)
                return self.base_request(options, data, params, retry_num - 1)
            else:
                logger.error(f"请求失败：{e}")
                return None

    def _orig_cookie_list_to_cookie_jar(self):
        """
        * 功能描述: 将原始的cookie字符串列表 (ORIGI_COOKIE_LIST) 转换成requests库的CookieJar对象
        * @fileName: login.py
        * @Author: Messiah
        * @Date: 2024/9/5 14:03
        """
        if self.orig_cookie_list:
            try:
                logger.info(f"发现用户自定义Cookie，执行转换。")
                for cookie_string in self.orig_cookie_list:
                    cookie_dict = {}
                    for item in cookie_string.split(";"):
                        key, value = item.strip().split("=", 1)
                        cookie_dict[key] = value
                    cookie_jar = requests.utils.cookiejar_from_dict(cookie_dict)
                    if cookie_jar not in self.cookie_list and type(cookie_jar) == type(RequestsCookieJar()):
                        self.cookie_list.append(cookie_jar)
                logger.success(f"Cookie转换成功。")
                logger.debug(f"Cookie转换成功：{self.cookie_list}")
            except Exception as e:
                logger.error(f"发生错误：{e}")
                logger.error(f"自定义Cookie转换失败! 请检查或重新设置Cookie。")
                raise Exception(f"自定义Cookie转换失败! 请检查或重新设置Cookie。")
        else:
            logger.error(f"本地Cookie为空,请在设置中更新!")
            raise Exception(f"本地Cookie为空,请在设置中更新!")

    def get_user_id(self):
        resp = self.base_request({"url": PixivConstant.HOST_URL}).text
        try:
            pattern = re.compile(r'user_id\s*:\s*["\'](\d+)["\']')
            match = pattern.search(resp)
            if match:
                user_id = match.group(1)
                logger.success(f"找到user_id：{user_id}")
                return user_id
            else:
                raise Exception(f"未找到user_id")
        except Exception as e:
            logger.error(f"发生错误：{e}")
            raise Exception(f"发生错误：{e}")

    def generate_client(self):
        """
        * 功能描述: 用于在启动多进程前,获取并校验cookie和uid
        * @fileName: login.py
        * @Author: Messiah
        * @Date: 2024/9/5 14:06
        """
        self.cookie = random.choice(self.cookie_list)
        logger.debug(f"随机获取一个Cookie:{self.cookie}")
        logger.info(f"开始获取账号ID。")
        self.user_id = self.get_user_id()
        logger.success(f"获取账号ID：{self.user_id}")
        logger.success(f"Pixiv客户端初始化完成!")
