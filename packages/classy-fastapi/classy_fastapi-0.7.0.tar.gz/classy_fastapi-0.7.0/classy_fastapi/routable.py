import dataclasses
import inspect
from functools import partial
from typing import Any, Callable, List, TypeVar

from fastapi.routing import APIRouter

from .route_args import EndpointDefinition, EndpointType

AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])


class Routable:
    """Base class for all classes the want class-based routing.

    This uses various decorators like @get or @post from the decorators module. The decorators just mark a method as
    an endpoint. __init_subclass__ then converts those to a list of desired endpoints in the _endpoints class method
    during class creation. The constructor constructs an APIRouter and adds all the routes in the _endpoints to it
    so they can be added to an app via FastAPI.include_router or similar.
    """
    _endpoints: List[EndpointDefinition] = []

    def __init_subclass__(cls) -> None:
        endpoints: list[EndpointDefinition] = []
        for obj_name in dir(cls):
            obj = getattr(cls, obj_name)
            if inspect.isfunction(obj) and hasattr(obj, '_endpoint'):
                endpoints.append(obj._endpoint)
        cls._endpoints = endpoints

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.router = APIRouter(*args, **kwargs)
        for endpoint in self._endpoints:
            if endpoint.type() == EndpointType.WEBSOCKET:
                self.router.add_api_websocket_route(path=endpoint.args.path,
                                                    endpoint=partial(endpoint.endpoint, self),
                                                    name=endpoint.args.name)
            else:
                self.router.add_api_route(endpoint=partial(endpoint.endpoint, self),
                                          **dataclasses.asdict(endpoint.args))
