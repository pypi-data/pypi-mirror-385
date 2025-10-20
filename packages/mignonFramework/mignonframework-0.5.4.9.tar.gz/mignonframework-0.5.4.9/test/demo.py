from mignonFramework import LoguruPlus, SendLog, RequestsMapping
from flask import Flask

RequestsMapping.set_framework(RequestsMapping.Stamp.FLASK)
loguru = LoguruPlus(level=LoguruPlus.INFO)
loguru.add_main_log_file("app", level=LoguruPlus.DEBUG)

log = loguru.getLogger()

app = Flask(__name__)

# 代理掉werkzeug和所有注册的logger
loguru.setUpLogger()


@SendLog(loguru.ERROR, format=loguru.console_format)
def sendMessageToAny(message):
    # 发送到邮箱什么的
    pass


@app.route('/data', methods=['POST'])
@RequestsMapping.RequestBody()
def home(data):
    log.info(data)
    log.warning("Request received for the home page.")
    return "hello world"


@app.route('/info/<int:port>', methods=['POST'])
@RequestsMapping.RequestBody()
def test1(port, data):
    log.info(data)
    log.info(port)
    log.warning("Request received for the home page.")
    return "hello world"

@app.route("/test", methods=['GET'])
@RequestsMapping.RequestParams()
def test2(data, time):
    log.info(data)
    log.info(time)
    return "hello world"



if __name__ == '__main__':
    app.run(debug=True, port=12340, host='0.0.0.0')
