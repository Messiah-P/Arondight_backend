import json
from functools import partial

from common.log.log_manager import logger
from common.utils import time_utils
from common.utils.timer import Timer
from dao.models.pixiv.pixiv_prim_tag_model import PixivPrimTag
from dao.models.pixiv.pixiv_tag_model import PixivTag
from dao.service.pixiv import pixiv_prim_tag_service, pixiv_tag_service
from plugin.PixivAide.constants.pixiv_constant import PixivConstant
from dao.models.pixiv.pixiv_user_model import PixivUser
from plugin.PixivAide.enums.pixiv_rest_enum import PixivRestEnum
from common.context.context import Context


class Extractor:
    def __init__(self, client):
        self.class_name = self.__class__.__name__
        self.client = client
        self.daily_url = PixivConstant.DAILY_URL
        self.follow_url = PixivConstant.FOLLOW_URL.format(client.user_id)
        self.artworks_url = PixivConstant.ARTWORKS_URL
        self.all_illust_url = PixivConstant.ALL_ILLUST_URL
        self.artworks_url = PixivConstant.ARTWORKS_URL
        self.ajax_illust = PixivConstant.AJAX_ILLUST
        self.ajax_headers = PixivConstant.AJAX_HEADERS
        self.rest_list = [rest.state for rest in PixivRestEnum]


    def request_user_list(self, offset, rest):
        """
        * 功能描述: 按照偏移量获得limit范围内的画师
        * @fileName: extractor.py
        * @Author: Lancelot
        * @Date: 2024/11/21 14:45
        """
        err_count = 0
        err_limit = 10

        params = {
            "offset": offset,
            "limit": 100,
            "rest": rest,
        }
        while True:
            try:
                response = json.loads(self.client.base_request({"url": self.follow_url}, params=params).text)
                logger.debug(f"获取第{offset}-{offset + 100}位画师，响应内容为：{response}")
            except Exception as e:
                logger.warning(f"获取第{offset}-{offset + 100}位画师出错：{e}。")
                if err_count < err_limit:
                    err_count += 1
                    logger.info(f"获取第{offset}-{offset + 100}位画师，重试第{err_count}次。")
                    continue
                else:
                    logger.error(f"获取第{offset}-{offset + 100}位画师重试次数过多，退出。")
                    break
            else:
                user_list = response['body']['users']
                logger.debug(f"获取第{offset}-{offset + 100}位画师，提取用户信息为：{user_list}")
                return user_list

    def get_user_info_list(self):
        """
        * 功能描述: 获取所有关注画师的uid,userName,latest_id(最新的pid)
        * 返回结果：[{"uid":uid,"userName":userName,"latest_id":latest_id},...]
        * @fileName: crawler.py
        * @Author: Messiah
        * @Date: 2024/9/5 14:41
        """
        offset = 0
        pixiv_user_po_list = []

        for rest in self.rest_list:
            logger.info(f"开始获取关注类型为{rest}的画师。")
            while True:
                user_list = self.request_user_list(offset, rest=rest)
                if user_list:
                    for user in user_list:
                        pixiv_user_po = PixivUser(
                            user_id=int(user["userId"]),
                            user_name=user["userName"],
                            follow_ind=True,
                            follow_type=rest
                        )
                        # 画师/用户无作品
                        if not user["illusts"]:
                            pixiv_user_po.latest_pid = -1
                            logger.warning(f"画师：{user["userName"]}(uid:{user["userId"]})无作品。")
                        else:
                            pixiv_user_po.latest_pid = int(user["illusts"][0]["id"])
                        pixiv_user_po_list.append(pixiv_user_po)
                    offset += 100
                    continue
                else:
                    logger.info(f"获取所有{rest}关注完毕。")
                    break

        return pixiv_user_po_list

    def get_all_pid_list(self, pixiv_user_po):
        """
        * 功能描述: 获取画师的全部PID
        * @parm: user: 画师信息--字典
        * @return: user_illust_list: 所有作品的pid，存为list
        * @fileName: crawler.py
        * @Author: Messiah
        * @Date: 2024/9/5 16:16
        """
        illust_url = self.all_illust_url.format(pixiv_user_po.user_id)
        try:
            user_body = json.loads(self.client.base_request({"url": illust_url}).text)["body"]
            illusts = user_body.get("illusts", [])
            manga = user_body.get("manga", [])
            # 取所有作品的pid，存为list
            all_pid_list = [int(key) for key in
                            [dict(illusts) if len(manga) == 0 else dict(illusts, **manga)][0].keys()]
        except Exception as e:
            logger.warning(f"获取画师作品数据出错： {e}")
            return []
        else:
            return all_pid_list

    @staticmethod
    def extract_illust_metadata(metadata_context):
        """
        * 功能描述: 生成作品细节元数据
        * @parm: pid, body
        * @return: data: 元数据
        * @fileName: extractor.py
        * @Author: Messiah
        * @Date: 2024/11/24
        """
        pid = int(metadata_context.get("ajax.illust_details.id"))
        title = metadata_context.get("ajax.illust_details.title")
        user_id = int(metadata_context.get("ajax.author_details.user_id"))
        user_name = metadata_context.get("ajax.author_details.user_name")
        artwork_url = metadata_context.get("ajax.illust_details.meta.canonical")
        original_url = metadata_context.get("ajax.illust_details.url_big")
        other_urls = {"url": metadata_context.get("ajax.illust_details.url"),
                      "url_s": metadata_context.get("ajax.illust_details.url_s"),
                      "url_ss": metadata_context.get("ajax.illust_details.url_ss"),
                      "url_placeholder": metadata_context.get("ajax.illust_details.url_placeholder")}
        collect_type = metadata_context.get("collect_type")
        tag_list = []
        for display_tag in metadata_context.get("ajax.illust_details.display_tags"):
            if "translation" in display_tag.keys():
                # 有翻译版本的tag，将原本的tag和翻译后的一并放入
                tag_list.append({
                    "original": display_tag["tag"],
                    "translation": display_tag["translation"]
                })
            else:
                tag_list.append({
                    "original": display_tag["tag"],
                    "translation": None  # 没有翻译版本时，translation为None
                })
        page_count = int(metadata_context.get("ajax.illust_details.page_count"))
        illust_type = int(metadata_context.get("ajax.illust_details.type"))
        is_r18 = any(tag['original'] == 'R-18' for tag in tag_list)
        ai_type = int(metadata_context.get("ajax.illust_details.ai_type"))
        view_count = int(metadata_context.get("ajax.illust_details.rating_view"))
        bookmark_count = int(metadata_context.get("ajax.illust_details.bookmark_user_total"))
        like_count = int(metadata_context.get("ajax.illust_details.rating_count"))
        upload_timestamp = metadata_context.get("ajax.illust_details.upload_timestamp")
        create_date = time_utils.convert_timestamp(upload_timestamp, 'Asia/Shanghai')
        formatted_create_date = create_date.strftime("%Y-%m-%d %H:%M:%S")

        # 提取后的作品元数据
        illust_metadata = Context()
        illust_metadata.set("pid", pid)
        illust_metadata.set("title", title)
        illust_metadata.set("user_id", user_id)
        illust_metadata.set("user_name", user_name)
        illust_metadata.set("collect_type", collect_type)
        illust_metadata.set("artwork_url", artwork_url)
        illust_metadata.set("original_url", original_url)
        illust_metadata.set("other_urls", other_urls)
        illust_metadata.set("tag", tag_list)
        illust_metadata.set("page_count", page_count)
        illust_metadata.set("illust_type", illust_type)
        illust_metadata.set("is_r18", is_r18)
        illust_metadata.set("ai_type", ai_type)
        illust_metadata.set("view_count", view_count)
        illust_metadata.set("bookmark_count", bookmark_count)
        illust_metadata.set("like_count", like_count)
        illust_metadata.set("create_date", formatted_create_date)

        return illust_metadata

    def get_illust_metadata(self, pid, collect_type, rank_date=None, rank_position=None):
        """
        * 功能描述: 获取作品元数据
        * @parm: pid
        * @return: data: 作品数据,字典
        * @fileName: extractor.py
        * @Author: Messiah
        * @Date: 2024/11/24
        """
        metadata_context = Context()
        ajax_illust_url = self.ajax_illust.format(pid)
        ajax_response = self.client.base_request(options={"url": ajax_illust_url, "headers": self.ajax_headers})
        if ajax_response:
            try:
                ajax_response_json = json.loads(ajax_response.text, object_hook=Context)
                logger.debug(f"ajax_response_json: {ajax_response_json}")
                logger.success(f"作品[{pid}]ajax请求数据解析成功！")
            except json.decoder.JSONDecodeError:
                logger.error(f"Json数据解析失败 - {ajax_response.text}")
                raise Exception(f"Json数据解析失败 - {ajax_response.text}")
        else:
            logger.error(f"ajax请求{pid}数据响应为空。")
            raise Exception(f"ajax请求{pid}数据响应为空。")

        # 未登录
        if ajax_response_json.get("message") == "出现了未知错误":
            raise Exception(f"出现了未知错误。")

        # 访问成功但是响应错误结果则不更新不下载;
        if ajax_response_json.get("error"):
            raise Exception(ajax_response_json.get("message"))

        ajax_response_json = ajax_response_json.get("body")

        metadata_context.set("ajax", ajax_response_json)
        metadata_context.set("collect_type", collect_type)

        illust_metadata = self.extract_illust_metadata(metadata_context)
        illust_metadata.set("rank_date", rank_date)
        illust_metadata.set("rank_position", rank_position)
        return illust_metadata

    def fetch_page_content(self, url):
        try:
            response = self.client.base_request(options={"url": url})
            return json.loads(response.text, object_hook=Context)
        except Exception as e:
            logger.warning(f"获取日榜页失败：{e}")
            raise Exception(f"获取日榜页失败：{e}")

    def get_page_info_daily(self, page_num=5, max_retries=5):
        illust_rank_list = []
        for n in range(1, page_num + 1):
            url = f"{self.daily_url}&p={n}&format=json"
            logger.info(f"获取第{n}页插画：{url}")
            page_content = Timer(120).retry(partial(self.fetch_page_content, url))
            if page_content:
                illust_rank_list.extend([{"pid": item.get("illust_id"), "rank_position": item.get("rank")} for item in
                                         page_content.get("contents") if
                                         isinstance(item, dict)])
            else:
                logger.warning(f"第{n}页获取失败，跳过此页。")

        return illust_rank_list

    @staticmethod
    def handel_tags(scoped_session, illust_metadata):
        tag = illust_metadata.get("tag")
        if tag:
            for tag_data in tag:
                # 检查标签表
                pixiv_tag_po = PixivTag(tag=tag_data.get("original"),
                                        translation=tag_data.get("translation"))
                pixiv_tag_service.check_pixiv_tag(scoped_session, pixiv_tag_po)
                # 在关联表中创建关联
                pixiv_prim_tag_po = PixivPrimTag(pid=illust_metadata.get("pid"),
                                                 sn=illust_metadata.get("sn"),
                                                 user_id=illust_metadata.get("user_id"),
                                                 collect_type=illust_metadata.get("collect_type"),
                                                 tag=tag_data.get("original"))
                pixiv_prim_tag_service.check_pixiv_prim_tag(scoped_session, pixiv_prim_tag_po)
        else:
            logger.success(f"无标签需要处理。")
