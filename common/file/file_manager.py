import datetime
import glob
import os
import re
import time

from common.constants.file_constant import FileConstant
from common.log.log_manager import logger
from pathlib import Path


class FileManager(object):
    def __init__(self):
        self.project_name = FileConstant.PROJECT_NAME
        self.root_path = self._get_root_path()

    def _get_root_path(self):
        # 获取当前文件所在的目录
        current_path = os.path.abspath(os.path.dirname(__file__))
        # 查找项目名称的位置
        project_index = current_path.find(self.project_name)
        return current_path[:project_index + len(self.project_name)]

    def generate_abs_file_path(self, file_path):
        abs_file_path = Path(self.root_path) / file_path
        if not abs_file_path.exists():
            abs_file_path.mkdir(parents=True)
        return abs_file_path

    @staticmethod
    def calc_size(size):
        """
        * 功能描述: 将文件大小转换为字节数
        * @parm: params size: 文件大小,字节数
        * @return: 文件大小
        * @fileName: file_manager.py
        * @Author: Messiah
        * @Date: 2024/11/24
        """
        if size / 1024 > 1024:
            return "%.3fMb" % (size / 1024 / 1024)
        else:
            return "%.3fKb" % (size / 1024)

    @staticmethod
    def write_content(full_path, content):
        """
        * 功能描述: 二进制数据写入图片
        * @parm: path: 图片路径
        * @return: content: content: 二进制数据
        * @return: 写入文件大小
        * @fileName: file_manager.py
        * @Author: Messiah
        * @Date: 2024/11/24
        """
        parent_dir = Path(full_path).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)
        with open(full_path, "wb") as f:
            f.write(content)
        return FileManager.calc_size(os.path.getsize(full_path))

    @staticmethod
    def modify_file_date(file_path, new_date):
        # 将ISO格式时间字符串转换为datetime对象
        datetime_obj = datetime.datetime.fromisoformat(new_date)
        # 将datetime对象转换为时间戳（秒）
        timestamp = time.mktime(datetime_obj.timetuple())
        # 获取文件的状态信息
        st_info = os.stat(file_path)
        # 使用os.utime更新文件的修改时间和访问时间（保留原来的访问时间）
        os.utime(file_path, (st_info.st_atime, timestamp))

    def is_exist_file(self, path, pattern):
        """
        * 功能描述: 查找pid是否已下载
        * @parm: path 画师路径/收藏作品主目录
        * @parm: mode: f"{uid}**/**{pid}**.**"
        * @return: True or False 已存在/不存在
        * @fileName: folder.py
        * @Author: Lancelot
        * @Date: 2024/11/22 19:57
        """
        abs_user_path = Path(self.root_path) / path
        result = glob.glob(os.path.join(abs_user_path, pattern))
        if result:
            return True
        else:
            return False

    def check_user_path(self, user_id, user_name):
        """
        * 功能描述: 寻找画师文件夹，如果没有则新建
        * @parm: uid: 画师id
        * @parm: user_name: 画师名称
        * @return: 画师所在文件夹路径
        * @fileName: folder.py
        * @Author: Messiah
        * @Date: 2024/9/6 17:40
        """
        # 避免画师更新名字,进行判断id，如果已经已经存在，则不创建
        abs_user_path = self.generate_abs_file_path(FileConstant.USER_PATH)
        for folder in os.listdir(abs_user_path):
            if str(user_id) == folder.split('_')[0]:
                user_path = Path(abs_user_path) / folder
                return user_path
        else:
            # 替换特殊字符为"_"
            user_name = re.sub(r'[\s/:*?"<>|\\]', '_', user_name)
            user_full_name = '_'.join([str(user_id), str(user_name)])
            user_path = Path(abs_user_path) / user_full_name
            user_path.mkdir(parents=True)
            logger.success("新增画师{}，创建目录{}".format(user_full_name, user_path))
            return user_path

    def check_download_path_without_mkidr(self):
        abs_dwld_path = self.generate_abs_file_path(FileConstant.DOWNLOAD_PATH)
        return abs_dwld_path

    def check_user_path_without_mkidr(self, user_id, user_name):
        abs_user_path = self.generate_abs_file_path(FileConstant.USER_PATH)
        for folder in os.listdir(abs_user_path):
            if str(user_id) == folder.split('_')[0]:
                user_path = Path(abs_user_path) / folder
                return user_path
        else:
            # 替换特殊字符为"_"
            user_name = re.sub(r'[\s/:*?"<>|\\]', '_', user_name)
            user_full_name = '_'.join([str(user_id), str(user_name)])
            user_path = Path(abs_user_path) / user_full_name
            return user_path

    def check_daily_path_without_mkidr(self, rank_date):
        abs_daily_path = self.generate_abs_file_path(FileConstant.DAILY_PATH)
        rank_date = datetime.datetime.strptime(rank_date, "%Y-%m-%d")
        daily_path = Path(abs_daily_path) / str(rank_date.year) / str(rank_date.month) / str(rank_date.day)
        return daily_path
