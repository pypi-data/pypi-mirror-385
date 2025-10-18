
from sqlalchemy import Column, Integer, String, Text, DateTime, text, UniqueConstraint

from serverz.server.database import Base

class Notes(Base):
    __tablename__ = 'notes' # 数据库中的表名，你可以改成你希望的名字

    # id (int, primary_key=True, autoincrement=True)
    # 你的属性表中 id 为 int, true (not null), true (primary key), 0 (length), ASC (key order), true (auto increment)
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True, # 自动递增
        nullable=False,     # 不能为空
        comment="自增"
    )

    timestamp = Column(
        DateTime,
        nullable=False,      # 不能为空
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP'),
        comment="时间戳"
    )
    content = Column(
        Text,               # TEXT 类型，适用于长文本
        nullable=False,     # 不能为空
        comment="内容"
    )
    
    # 定义 __repr__ 方法以便打印对象时有清晰的表示
    def __repr__(self):
        return (f"<Notes(id={self.id}, timestamp='{self.timestamp}',content='{self.content}' ")

