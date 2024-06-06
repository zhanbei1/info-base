import os

from fastapi import FastAPI
from langchain.schema.runnable import RunnableLambda
from langserve import add_routes
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from infobase.chain import get_chain
from infobase.configs import DEFAULT_BIND_HOST, PORT
from infobase.model import ChatRequestInput
from traceloop.sdk import Traceloop

Traceloop.init(app_name="desmond_test_traceloop",
               exporter=OTLPSpanExporter(endpoint="http://localhost:32167/api/v1/insert/trace-otlp",
                                         headers={"apikey": "2b326a3b-6a45-4081-a6c4-7b3d0b875c79"}),
               metrics_exporter=OTLPMetricExporter(endpoint="http://localhost:32167/api/v1/insert/metric-otlp",
                                                   headers={"apikey": "2b326a3b-6a45-4081-a6c4-7b3d0b875c79"})
               )

app = FastAPI(
    title="InfoBase",
    version="0.0.1",
    # Code Warehouse Assistant. Assist students in product development, testing,
    # and delivery to quickly understand project functionality and content, review requirements and PR content,
    # assist in troubleshooting problems, and provide preliminary solutions
    description="代码仓库助手。协助产品，开发，测试，交付同学快速了解项目功能和内容，审核需求和PR内容，协助排查问题并给出初步解决方案"
)

add_routes(
    app,
    RunnableLambda(get_chain),
    config_keys=["configurable"],
    input_type=ChatRequestInput,
    output_type=str
)

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    # 加载环境配置文件.env
    load_dotenv()
    uvicorn.run(app, host=DEFAULT_BIND_HOST, port=PORT)
