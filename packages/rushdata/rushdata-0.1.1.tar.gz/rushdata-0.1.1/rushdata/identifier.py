from rushdata.utils import vali


class Identifier:
    def __init__(self, namespace: str, value: str):
        if not vali(namespace):
            raise ValueError(f"命名空间 '{namespace}' 包含非法字符，只允许 0-9, a-z, A-Z, _, /")

        self._namespace = namespace
        self._value = value

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def value(self) -> str:
        return self._value

    @staticmethod
    def from_str(string: str) -> 'Identifier':
        namespace, value = string.split(":", 1)
        return Identifier(namespace, value)
