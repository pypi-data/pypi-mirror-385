from rushdata.identifier import Identifier
from rushdata.resource.data import ResourceType


class ResourceManager:
    def __init__(self, root: str):
        self.root = root
        self.resources = []

    def add(self, resource_type_class):
        if resource_type_class not in self.resources:
            self.resources.append(resource_type_class(self.root))

    def get(self, name: str, value):
        for resource in self.resources:
            if resource.name == name:
                return resource.get(Identifier.from_str(str(value)))

        return None
