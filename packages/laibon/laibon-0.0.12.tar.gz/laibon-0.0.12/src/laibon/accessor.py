# Copyright Wenceslaus Mumala 2023. See LICENSE file.

from laibon import common
from laibon import exception


class DelayedExceptionAccessor:
    _KEY = common.ContainerKey("DelayedException")

    @staticmethod
    def set(data, data_container: common.Container):
        if data is None:
            raise exception.InvalidArgumentException("Cannot set a null object")
        data_container.put(DelayedExceptionAccessor._KEY, data)

    @staticmethod
    def get(data_container: common.Container):
        return data_container.get(DelayedExceptionAccessor._KEY)
