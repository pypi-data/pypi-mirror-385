# @Coding: UTF-8
# @Time: 2024/9/24 12:58
# @Author: xieyang_ls
# @Filename: annotation.py

from argparse import ArgumentTypeError

from http.server import BaseHTTPRequestHandler

from pyutils_spirit.exception.exception import NoneSignatureError

from pyutils_spirit.spirit_container.spirit_application_container import SpiritApplicationContainer


class ContainerAnnotation:
    spirit_application_container: SpiritApplicationContainer = SpiritApplicationContainer()

    @classmethod
    def resource(cls, names: list[str] | str) -> callable:
        if not isinstance(names, list | str):
            raise ValueError("Resource: the signature of type must be list or str")
        if not all(isinstance(name, str) for name in names):
            raise ValueError("All elements in the list must be strings")
        if len(names) == 0:
            raise ValueError("the names must not be empty")

        def decorator_func(func):
            def wrapper(*args, **kwargs):
                if isinstance(names, str):
                    resources = cls.spirit_application_container.get_resource(signature=names)
                    if resources is None:
                        raise ValueError(f"the signature {names} does not exist")
                else:
                    resources = kwargs["resources"]
                    for name in names:
                        instance = cls.spirit_application_container.get_resource(signature=name)
                        if instance is None:
                            raise ValueError(f"the signature {name} does not exist")
                        resources[name] = instance
                func(args[0], resources)

            wrapper.__decorator__ = "Resource"
            return wrapper

        return decorator_func

    @classmethod
    def get(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('GET Method: path should be a string')
        if len(path) == 0:
            raise ValueError('GET Method: path should not be empty')

        def decorator_get_func(func):
            func.__decorator__ = "GET"
            func.__decorator_path__ = path
            return func

        return decorator_get_func

    @classmethod
    def post(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('POST Method: path should be a string')
        if len(path) == 0:
            raise ValueError('POST Method: path should not be empty')

        def decorator_post_func(func):
            func.__decorator__ = "POST"
            func.__decorator_path__ = path
            return func

        return decorator_post_func

    @classmethod
    def put(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('PUT Method: path should be a string')
        if len(path) == 0:
            raise ValueError('PUT Method: path should not be empty')

        def decorator_put_func(func):
            func.__decorator__ = "PUT"
            func.__decorator_path__ = path
            return func

        return decorator_put_func

    @classmethod
    def delete(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('DELETE Method: path should be a string')
        if len(path) == 0:
            raise ValueError('DELETE Method: path should not be empty')

        def decorator_delete_func(func):
            func.__decorator__ = "DELETE"
            func.__decorator_path__ = path
            return func

        return decorator_delete_func


class Component:
    def __init__(self, signature: str) -> None:
        if not isinstance(signature, str):
            raise NoneSignatureError
        if len(signature) == 0:
            raise ValueError("Component: Signature cannot be empty")
        self.__signature: str = signature

    def __call__(self, component_cls: type[object]) -> type[object]:
        component_cls.__decorator__ = "Component"

        def wrapper_component(__cls: type[object]) -> object:
            __component: object = (ContainerAnnotation.spirit_application_container
                                   .get_resource(signature=self.__signature))
            if __component is None:
                __component = object.__new__(__cls)
                ContainerAnnotation.spirit_application_container.set_resource(signature=self.__signature,
                                                                              resource=__component)
            return __component

        component_cls.__new__ = wrapper_component
        return component_cls


class Mapper:
    def __init__(self, signature: str) -> None:
        if not isinstance(signature, str):
            raise NoneSignatureError
        if len(signature) == 0:
            raise ValueError("Mapper: Signature cannot be empty")
        self.__signature: str = signature

    def __call__(self, mapper_cls: type[object]) -> type[object]:
        mapper_cls.__decorator__ = "Mapper"

        def wrapper_mapper(__cls: type[object]) -> object:
            __mapper: object = (ContainerAnnotation.spirit_application_container
                                .get_resource(signature=self.__signature))
            if __mapper is None:
                __mapper = object.__new__(__cls)
                ContainerAnnotation.spirit_application_container.set_resource(signature=self.__signature,
                                                                              resource=__mapper)
            return __mapper

        mapper_cls.__new__ = wrapper_mapper
        return mapper_cls


class Service:
    def __init__(self, signature: str) -> None:
        if not isinstance(signature, str):
            raise NoneSignatureError
        if len(signature) == 0:
            raise ValueError("Service: Signature cannot be empty")
        self.__signature: str = signature

    def __call__(self, service_cls: type[object]) -> type[object]:
        service_cls.__decorator__ = "Service"

        def wrapper_service(__cls: type[object]) -> object:
            __service: object = (ContainerAnnotation.spirit_application_container
                                 .get_resource(signature=self.__signature))
            if __service is None:
                __service = object.__new__(__cls)
                ContainerAnnotation.spirit_application_container.set_resource(signature=self.__signature,
                                                                              resource=__service)
            return __service

        service_cls.__new__ = wrapper_service
        return service_cls


class Controller:
    def __init__(self, path: str) -> None:
        if not isinstance(path, str):
            raise NoneSignatureError
        if len(path) == 0:
            raise ValueError("Controller: path cannot be empty")
        self.__path: str = path

    def __call__(self, controller_cls: type[object]) -> type[object]:
        controller_cls.__decorator__ = "Controller"
        controller_cls.__decorator_path__ = self.__path

        def wrapper_controller(__cls: type[object]) -> object:
            __controller: object = (ContainerAnnotation.spirit_application_container
                                    .get_resource(signature=self.__path))
            if __controller is None:
                __controller = object.__new__(__cls)
                ContainerAnnotation.spirit_application_container.set_resource(signature=self.__path,
                                                                              resource=__controller)
            return __controller

        controller_cls.__new__ = wrapper_controller
        return controller_cls


class ExceptionAdvice:
    def __init__(self, exception_advice_cls: type) -> None:
        if not isinstance(exception_advice_cls, type):
            raise TypeError('ExceptionAdvice can only be applied to classes')
        exception_advice_cls.__decorator__ = "ExceptionAdvice"
        self.__exception_advice_cls: type = exception_advice_cls

    def __call__(self):
        self.__exception_advice_cls()

    @classmethod
    def throws_exception(cls, ex_type: type):
        if not isinstance(ex_type, type):
            raise TypeError("ThrowsException: argument 'ex' must be a type")

        def decorator_throws_exception_func(func) -> callable:
            func.__decorator__ = "ThrowsException"
            func.__decorator_params__ = ex_type
            return func

        return decorator_throws_exception_func


class RequestInterceptor:
    def __init__(self, interceptor_paths: set[str]) -> None:
        if not isinstance(interceptor_paths, set):
            raise TypeError('RequestInterceptor: interceptor_paths must be a set')
        for interceptor_path in interceptor_paths:
            if not isinstance(interceptor_path, str):
                raise TypeError('RequestInterceptor: interceptor_paths must be a string set')
        self.__interceptor_paths: set[str] = interceptor_paths

    def __call__(self, interceptor_cls: type) -> type:
        if not isinstance(interceptor_cls, type):
            raise TypeError('RequestInterceptor can only be applied to classes')
        interceptor_cls.__decorator__ = "RequestInterceptor"
        interceptor_cls.__decorator_params__ = self.__interceptor_paths
        return interceptor_cls

    @classmethod
    def interceptor_before(cls) -> callable:
        def decorator_request_func(func) -> callable:

            def interceptor_before_method(it_self: object, request: BaseHTTPRequestHandler) -> tuple[int, bool]:
                if (not isinstance(request, BaseHTTPRequestHandler) and
                        not isinstance(it_self, BaseHTTPRequestHandler)):
                    raise ArgumentTypeError('InterceptorBefore: argument must be BaseHTTPRequestHandler Type')
                request.headers["X-Intercepted"] = "True"
                response_code, response_status = func(it_self, request)
                if not isinstance(response_code, int) or not isinstance(response_status, bool):
                    err: str = 'InterceptorBefore: return value must be (response_code: int, response_status: bool)'
                    raise ValueError(err)
                return response_code, response_status

            interceptor_before_method.__decorator__ = "InterceptorBefore"
            return interceptor_before_method

        return decorator_request_func

    @classmethod
    def interceptor_after(cls) -> callable:
        def decorator_request_func(func) -> callable:
            def interceptor_after_method(it_self: object, request: BaseHTTPRequestHandler) -> None:
                if not isinstance(request, BaseHTTPRequestHandler) and not isinstance(it_self,
                                                                                      BaseHTTPRequestHandler):
                    raise ArgumentTypeError('InterceptorAfter: argument should be BaseHTTPRequestHandler Type')
                func(it_self, request)
                return None

            interceptor_after_method.__decorator__ = "InterceptorAfter"
            return interceptor_after_method

        return decorator_request_func


resource = ContainerAnnotation.resource
get = ContainerAnnotation.get
post = ContainerAnnotation.post
put = ContainerAnnotation.put
delete = ContainerAnnotation.delete
throws_exception = ExceptionAdvice.throws_exception
before = RequestInterceptor.interceptor_before
after = RequestInterceptor.interceptor_after
