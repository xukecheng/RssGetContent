from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import aioredis
import os
import RssGetContent

app = FastAPI()
templates = Jinja2Templates(directory="templates")


async def get_redis_pool():
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis = await aioredis.from_url(
        f"redis://{redis_host}:{redis_port}/1?encoding=utf-8",
        decode_responses=True)
    return redis


@app.on_event('startup')
async def startup_event():
    """
    获取链接
    :return:
    """
    app.state.redis = await get_redis_pool()


@app.on_event('shutdown')
async def shutdown_event():
    """
    关闭
    :return:
    """
    app.state.redis.close()
    await app.state.redis.wait_closed()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/gamersky")
async def gamersky(url: str):
    try:
        return {
            "code": 200,
            "data": RssGetContent.GamerSky(url=url).getContent(),
            "message": "success"
        }
    except Exception:
        return {"code": 200, "data": "参数错误", "message": "success"}


@app.get("/notion", response_class=HTMLResponse)
async def notion(request: Request, url: str):
    rget = await request.app.state.redis.get(url)
    if rget and rget != "error":
        print("RssGetContent.Notion 已获取过该 URL")
        html_content = rget
    else:
        print("RssGetContent.Notion 没有获取过该 URL")
        html_content = RssGetContent.Notion(url=url).getPageHtml()
        await request.app.state.redis.set(url, html_content, ex=2592000)

    return templates.TemplateResponse("item.html", {
        "request": request,
        "html_content": html_content,
        "url": url
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app',
                host="0.0.0.0",
                port=9000,
                reload=True,
                debug=True)
