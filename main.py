import flask, json, os
from flask import request
import RssGetContent

server = flask.Flask(__name__)


@server.route('/gamersky', methods=['get'])
def gamersky():
    try:
        url = request.values.get('url')
        return {
            "code": 200,
            "data": RssGetContent.GamerSky(url=url).getContent(),
            "message": "success"
        }
    except AttributeError:
        return {"code": 200, "data": "参数错误", "message": "success"}


if __name__ == '__main__':
    server.run(debug=True, port=8999, host='0.0.0.0', processes=os.cpu_count())
