from common.constants.file_constant import FileConstant
from common.file.file_manager import FileManager
from common.log.log_manager import logger

def categorize_by_user(uid, pid):
    file_manager = FileManager()
    # TODO 若插画已下载，在数据库中更新，这里暂时跳过
    if file_manager.is_exist_file(
            FileConstant.USER_PATH, f"{uid}**/**{pid}**.**"):
        logger.info(f"作品uid:{uid} - pid:{pid}已存在。")
        return
