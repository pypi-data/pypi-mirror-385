# @Coding: UTF-8
# @Time: 2025/3/28 23:50
# @Author: xieyang_ls
# @Filename: thread_holder.py

from threading import current_thread

from typing import TypeVar, Generic, Iterator

from pyutils_spirit.util.assemble import Assemble, HashAssemble

K = TypeVar('K')

V = TypeVar('V')


class ThreadHolder(Generic[K, V]):

    def __init__(self):
        self.__holders: Assemble[int | K, V] = HashAssemble()

    def __len__(self) -> int:
        return len(self.__holders)

    def __iter__(self) -> Iterator[int | K]:
        return iter(self.__holders)

    def __next__(self) -> int | K:
        return self.__holders.__next__()

    def set_thread_holder(self, instance: V) -> None:
        current_thread_id: int = current_thread().ident
        self.__holders[current_thread_id] = instance

    def get_thread_holder(self) -> V:
        current_thread_id = current_thread().ident
        return self.__holders[current_thread_id]

    def remove_thread_holder(self) -> V:
        current_thread_id = current_thread().ident
        return self.__holders.remove(key=current_thread_id)

    def set_holder(self, key: K, value: V) -> None:
        self.__holders[key] = value

    def get_holder(self, key: K) -> V:
        return self.__holders[key]

    def remove_holder(self, key: K) -> V:
        return self.__holders.remove(key=key)
