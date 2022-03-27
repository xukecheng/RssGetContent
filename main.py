from fastapi import FastAPI, Request
import RssGetContent
from fastapi.responses import HTMLResponse
import redis
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/gamersky")
def gamersky(url: str):
    try:
        return {
            "code": 200,
            "data": RssGetContent.GamerSky(url=url).getContent(),
            "message": "success"
        }
    except Exception:
        return {"code": 200, "data": "参数错误", "message": "success"}


@app.get("/notion", response_class=HTMLResponse)
def notion(request: Request, url: str):
    pool = redis.ConnectionPool(host='10.10.10.2',
                                port=6379,
                                db=1,
                                decode_responses=True)
    r = redis.StrictRedis(connection_pool=pool)
    rget = r.get(url)
    if rget and rget != "error":
        print("RssGetContent.Notion 已获取过该 URL")
        html_content = rget
    else:
        print("RssGetContent.Notion 没有获取过该 URL")
        html_content = RssGetContent.Notion(url=url).getPageHtml()

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
