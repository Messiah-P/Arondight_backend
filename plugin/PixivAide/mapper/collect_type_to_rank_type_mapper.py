from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_rank_type_enum import PixivRankTypeEnum


class CollectToRankMapper:
    collect_to_rank = {
        PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_2.code: PixivRankTypeEnum.PIXIV_RANK_TYPE_0.code,
        PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_3.code: PixivRankTypeEnum.PIXIV_RANK_TYPE_1.code,
        PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_4.code: PixivRankTypeEnum.PIXIV_RANK_TYPE_2.code
    }

    @classmethod
    def get_rank_type(cls, collect_type):
        return cls.collect_to_rank.get(collect_type)
