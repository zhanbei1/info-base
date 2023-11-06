# httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
HTTPX_DEFAULT_TIMEOUT = 300.0

# API 是否开启跨域，默认为False，如果需要开启，请设置为True
# is open cross domain
OPEN_CROSS_DOMAIN = False

# 各服务器默认绑定host 和 端口
DEFAULT_BIND_HOST = "0.0.0.0"
PORT = 8001

# webui.py server
WEBUI_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 8501,
}

# api.py server
API_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 7861,
}

# 本地下拉git仓库之后 ，存放的目录
GIT_CLONE_PATH = "tmp/git_repository/"

# 向量数据库配置
MILVUS_CONFIG = {
    "host": "127.0.0.1",
    "port": "19530",
    "user": "",
    "password": "",
    "secure": False,
}
