from typing import Optional
from fastapi import FastAPI
import RssGetContent
from fastapi.responses import HTMLResponse

app = FastAPI()


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


@app.get("/notion")
def notion(url: str):
    html_content = RssGetContent.Notion(url=url).getPageHtml()
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app',
                host="0.0.0.0",
                port=9000,
                reload=True,
                debug=True)
