class PixivConstant:

    # Host
    HOST_URL = "https://www.pixiv.net"

    # 链接：日榜地址
    DAILY_URL = "https://www.pixiv.net/ranking.php?mode=daily&content=illust"
    # 链接：获取关注画师列表
    FOLLOW_URL = "https://www.pixiv.net/ajax/user/{}/following"
    # 链接：获取画师所有作品
    ALL_ILLUST_URL = "https://www.pixiv.net/ajax/user/{}/profile/all"
    # 链接：获取作品
    ARTWORKS_URL = "https://www.pixiv.net/artworks/{}"
    # 链接：多图-每张图的url组
    MULTI_URL = "https://www.pixiv.net/ajax/illust/{}/pages"
    # 链接：动图的zip包下载链接
    UGOIRA_URL = "https://www.pixiv.net/ajax/illust/{}/ugoira_meta"
    # 链接：获取作品信息
    AJAX_ILLUST = "https://www.pixiv.net/touch/ajax/illust/details?illust_id={}"
    # Headers：获取作品信息
    AJAX_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "",
        "Connection": "keep-alive",
    }
