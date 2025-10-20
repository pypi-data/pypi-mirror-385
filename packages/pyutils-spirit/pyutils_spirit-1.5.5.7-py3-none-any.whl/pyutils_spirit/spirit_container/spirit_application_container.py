from typing import Any

from pyutils_spirit.util.assemble import Assemble, HashAssemble

from pyutils_spirit.exception.exception import ArgumentException

from pyutils_spirit.util.cities import get_all_cities, get_cities, get_provinces


class SpiritApplicationContainer:
    __instance: Any = None

    __application_container: Assemble[str, Any] = None

    def __init__(self):
        if self.__application_container is None:
            self.__application_container = HashAssemble()

    def __new__(cls) -> object:
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def set_resource(self, signature: str, resource: Any):
        if signature in self.__application_container:
            raise ArgumentException(f"spirit_application_container: '{signature}' "
                                    f"Different resources cannot have the same signature")
        self.__application_container[signature] = resource

    def get_resource(self, signature: str) -> Any:
        return self.__application_container[signature]

    def remove_resource(self, signature: str) -> Any:
        return self.__application_container.remove(key=signature)

    def get_capacity(self):
        return len(self.__application_container)

    @classmethod
    def wired_container(cls, signature: str, resource_cls: type) -> None:
        if cls.__instance is None:
            cls.__instance = SpiritApplicationContainer()

        def wired_resource(other_cls) -> object:
            instance = cls.__instance.get_resource(signature=signature)
            if instance is None:
                instance = object.__new__(other_cls)
                cls.__instance.set_resource(signature=signature, resource=instance)
            return instance

        resource_cls.__new__ = wired_resource
        resource_cls()

    def __len__(self):
        return len(self.__application_container)

    def __iter__(self):
        return iter(self.__application_container)

    def __next__(self):
        return next(self.__application_container)


class CityComponent:
    def __init__(self):
        self.get_cities: callable = get_cities
        self.get_province: callable = get_provinces
        self.get_all_cities: callable = get_all_cities


SpiritApplicationContainer.wired_container(signature="city_component", resource_cls=CityComponent)
