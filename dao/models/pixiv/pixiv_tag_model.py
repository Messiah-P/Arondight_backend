from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column
from common.database.db_connector import Base


class PixivTag(Base):
    __tablename__ = 'pixiv_tag'

    tag: Mapped[str] = mapped_column(String(255), primary_key=True, nullable=False, comment='标签')
    translation: Mapped[str] = mapped_column(String(255), nullable=True, comment='标签翻译')

    __table_args__ = (
        Index('index_translation', 'translation'),
    )

    @staticmethod
    def generate_pixiv_tag_po(pixiv_tag_context):
        return PixivTag(tag=pixiv_tag_context.get("tag"),
                        translation=pixiv_tag_context.get("translation"), )
