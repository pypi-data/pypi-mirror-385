from abc import ABC
from pathlib import Path

from rushdata.identifier import Identifier
from rushdata.utils import vali


class ResourceType(ABC):
    def __init__(self, root: str):
        self.types = []
        self.root = root

        self.add_default()

    @property
    def name(self):
        raise NotImplementedError()

    def add_default(self):
        pass

    def create_type(self, type_name):
        if not vali(type_name):
            raise ValueError(f"类型名称 '{type_name}' 包含非法字符")

        if type_name not in self.types:
            self.types.append(type_name)

    def get(self, iden: Identifier, _t: str = None):
        namespace = iden.namespace
        value = iden.value

        if _t is None:
            _type = None
        else:
            if not _t in self.types:
                raise ValueError()
            _type = _t

        return Path(f'{self.name}/{self.root}/{namespace}/{f'{_type}/' if _type is not None else ''}{value}')
