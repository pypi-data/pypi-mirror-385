# 辅助读书做笔记的插件服务
from fastapi import APIRouter, Depends, HTTPException, status, Header
import os
import datetime
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from serverz.server.database import Base, Notes

from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

@contextmanager
def create_session(engine):
    # 5. 创建会话 (Session)
    # Session 是与数据库交互的主要接口，它管理着你的对象和数据库之间的持久化操作
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback() # 发生错误时回滚事务
    finally:
        session.close() # 关闭会话，释放资源


async def check_current_user(token: str = Header(...)):
    if token != os.getenv("token"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid X-Token header")
    return {"username":"zxf"}

router = APIRouter(
    tags=["Reader"],
    dependencies = [Depends(check_current_user)]
)

database_url = os.getenv('database_url')
engine = create_engine(database_url, echo=False) # echo=True 仍然会打印所有执行的 SQL 语句
Base.metadata.create_all(engine)


@router.get('/')
async def get_status():
    return "running"

class BookTips(BaseModel):
    text: str

def get_contents(session):
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min) # 今天 00:00:00
    tomorrow_start = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time.min) # 明天 00:00:00
    contents = session.query(Notes).filter(Notes.timestamp >= today_start, Notes.timestamp < tomorrow_start).order_by(Notes.timestamp.asc()).all()  # 排序
    return contents
    

@router.post('/record')
async def record(request: BookTips):
    text = request.text
    with create_session(engine) as session:
        contents = get_contents(session)
        if contents:
            latest_content = contents[-1]
            old_text = latest_content.content
            if old_text[:-2] in text:
                latest_content.content = text
            else:
                note = Notes(content = text,
                    timestamp = datetime.datetime.now(),
                    )
                session.add(note)
        else:
            note = Notes(content = text,
                    timestamp = datetime.datetime.now(),
                    )
            session.add(note)
        session.commit()

    return "successful"


@router.get('/read')
async def read():
    with create_session(engine) as session:
        contents = get_contents(session)
        content_list = [i.content for i in contents]
        content = '\n\n'.join(content_list)
        return content


