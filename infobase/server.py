from fastapi import FastAPI
from langserve import add_routes

from infobase.chain import get_chain
from infobase.configs import DEFAULT_BIND_HOST, PORT

app = FastAPI()

add_routes(
    app,
    get_chain(),
    config_keys=["tags"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=DEFAULT_BIND_HOST, port=PORT)


class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
