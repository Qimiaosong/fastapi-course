from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

# 用于根据定义的 ORM 模型类自动在数据库中创建表结构
models.Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
    

my_posts = [{"title":"万神殿","content":"Upload Intelligence","ID":1},
            {"title":"再见💞","content":"葛夕留几手无视麦0","ID":2}]


@app.get("/")
async def root():
    return {"message":"月入3万的offer!来吧！！！"}

