import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from .decorators import get, post, websocket
from .routable import Routable


class ExampleRoutableBase(Routable):
    def __init__(self, injected: int) -> None:
        super().__init__()
        self._injected = injected

    @get(path='/add/{x}')
    def add(self, x: int) -> int:
        return x + self._injected

    @post(path='/sub/{x}')
    def sub(self, x: int) -> int:
        return x - self._injected

    @get(path='/async')
    async def do_async(self) -> int:
        await asyncio.sleep(0.1)
        return self._injected + 1

    @get(path='/aecho/{val}', response_class=PlainTextResponse)
    async def aecho(self, val: str) -> str:
        await asyncio.sleep(0.1)
        return f'{val} {self._injected}'

    @websocket("/ws/aecho")
    async def websocket_aecho(self, websocket: WebSocket) -> None:
        await websocket.accept()
        val = await websocket.receive_text()
        await websocket.send_text(f'{val} {self._injected + 1}')
        await websocket.close()


class ExampleRoutable(ExampleRoutableBase):
    @get(path='/mul/{x}')
    def mul(self, x: int) -> int:
        return x * self._injected

    @post(path='/div/{x}')
    def div(self, x: int) -> int:
        return int(x / self._injected)


class ExampleRoutable2(ExampleRoutableBase):
    @post(path='/div/{x}')
    def div(self, x: int) -> int:
        return x // self._injected


def test_routes_respond() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.get('/add/22')
    assert response.status_code == 200
    assert response.text == '24'

    response = client.post('/sub/4')
    assert response.status_code == 200
    assert response.text == '2'


def test_routes_only_respond_to_method() -> None:
    """If the methods are defined as GET they shouldn't respond to POST, etc."""
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.post('/add/22')
    assert response.status_code == 405
    response = client.put('/add/22')
    assert response.status_code == 405
    response = client.delete('/add/22')
    assert response.status_code == 405

    response = client.get('/sub/4')
    assert response.status_code == 405
    response = client.put('/sub/4')
    assert response.status_code == 405
    response = client.delete('/sub/4')
    assert response.status_code == 405


def test_routes_exclusive_to_subclasses() -> None:
    """We want our routes to be inheritable so you can have a base class and then subclasses of that base class will
    have the same routes as the base class plus any additional routes added. This test ensures that if you have 2
    different sub-classes of a base class their routes are separate and we're not accidentally adding the routes from
    one subclass to a different one.
    """
    app = FastAPI()
    app2 = FastAPI()
    t = ExampleRoutable(2)
    t2 = ExampleRoutable2(2)
    app.include_router(t.router)
    app2.include_router(t2.router)

    client = TestClient(app)
    client2 = TestClient(app2)

    response = client.get('/mul/3')
    assert response.status_code == 200
    assert response.text == '6'

    response = client2.get('/mul/3')
    assert response.status_code == 404

    response = client.post('/div/-1')
    assert response.status_code == 200
    assert response.text == '0'

    response = client2.post('/div/-1')
    assert response.status_code == 200
    assert response.text == '-1'


def test_async_methods_work() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.get('/async')
    assert response.status_code == 200
    assert response.text == '3'

    # Make sure we can call it more than once.
    response = client.get('/async')
    assert response.status_code == 200
    assert response.text == '3'


def test_async_methods_with_args_work() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.get('/aecho/hello')
    assert response.status_code == 200
    assert response.text == 'hello 2'


def test_async_websocket_methods_with_args_work() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)
    with client.websocket_connect("/ws/aecho") as websocket:
        websocket.send_text('hello')
        assert websocket.receive_text() == 'hello 3'
