"""
* 功能描述: Bark通知模块
* @fileName: bark.py
* @Author: Lancelot
* @Date: 2024/10/28 15:14
"""

import requests
from typing import Optional, Union, Tuple


class Bark:
    def __init__(self,
                 bark_url: Optional[str] = None,
                 pic_url: Optional[str] = None,
                 title: Optional[str] = None,
                 group: Optional[str] = None):
        self.bark_url = bark_url
        self.pic_url = pic_url
        self.title = title
        self.group = group

    """
    * 功能描述: 更新参数
    * @parm: bark_url, pic_url, title, group
    * @return: 
    * @fileName: bark.py
    * @Author: Lancelot
    * @Date: 2024/10/28 15:15
    """

    def update_params(self,
                      bark_url: Optional[str] = None,
                      pic_url: Optional[str] = None,
                      title: Optional[str] = None,
                      group: Optional[str] = None):
        if bark_url:
            self.bark_url = bark_url
        if pic_url:
            self.pic_url = pic_url
        if title:
            self.title = title
        if group:
            self.group = group

    """
    * 功能描述: 发送通知
    * @parm: message
    * @return: 
    * @fileName: bark.py
    * @Author: Lancelot
    * @Date: 2024/10/28 15:16
    """

    def notice(self,
               bark_url: Optional[str] = None,
               pic_url: Optional[str] = None,
               title: Optional[str] = None,
               group: Optional[str] = None,
               url: Optional[str] = None,
               message: Optional[str] = None,
               timeout: Union[float, Tuple[float, float]] = (2.0, 3.0)):

        bark_url = bark_url or self.bark_url
        pic_url = pic_url or self.pic_url
        title = title or self.title
        group = group or self.group

        if not bark_url or not pic_url:
            raise ValueError("默认Bark URL 、 title 和 pic_url必须在通知前初始化。")

        req_url = f"{bark_url}/{title}/{message}?icon={pic_url}"
        if group:
            req_url += f"&group={group}"
        if url:
            req_url += f"&url={url}"

        with requests.Session() as req:
            try:
                response = req.get(req_url, timeout=timeout)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Bark通知请求失败: {e}")
