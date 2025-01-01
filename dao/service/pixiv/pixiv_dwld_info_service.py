from dao.dos.pixiv import pixiv_dwld_info_dos
from common.database.transaction import get_session
from plugin.PixivAide.enums.pixiv_download_status_enum import PixivDownloadStatusEnum


def insert(scoped_session, pixiv_dwld_info_po):
    return pixiv_dwld_info_dos.insert(get_session(scoped_session), pixiv_dwld_info_po)


def select_by_primary_key(scoped_session, pixiv_dwld_info_po):
    return pixiv_dwld_info_dos.select_by_primary_key(get_session(scoped_session), pixiv_dwld_info_po)


def update_by_primary_key_selective(scoped_session, pixiv_dwld_info_po):
    return pixiv_dwld_info_dos.update_by_primary_key_selective(get_session(scoped_session), pixiv_dwld_info_po)


def select_undownloaded_task_by_pid_and_collect_type(scoped_session, pid, collect_type):
    return pixiv_dwld_info_dos.select_undownloaded_task_by_pid_and_collect_type(get_session(scoped_session), pid, collect_type,
                                                        PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_1.code)


def select_undownloaded_task_by_collect_type(scoped_session, collect_type):
    return pixiv_dwld_info_dos.select_undownloaded_task_by_collect_type(get_session(scoped_session), collect_type,
                                                                        PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_1.code)


def lock_download_task(scoped_session, pixiv_dwld_info_po):
    return pixiv_dwld_info_dos.lock_download_task(get_session(scoped_session), pixiv_dwld_info_po)


def unlock_download_task(scoped_session, pixiv_dwld_info_po):
    return pixiv_dwld_info_dos.unlock_download_task(get_session(scoped_session), pixiv_dwld_info_po)
