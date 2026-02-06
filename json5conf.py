__all__ = (
    'json5_read',
    'JSONConfDict',
    'InvalidJSONError',
)

import json5

class InvalidJSONError(ValueError):
    def __init__(self, message, file_path):
        self.file_path = file_path
        # Keep the original message
        super().__init__(message)

class JSONCompatLoader(json5.loader.DefaultLoader):
# This loader imports identifiers as raw strings
# compatible with the standard json module
    @json5.loader.DefaultLoader.load.register(json5.model.Identifier)
    def identifier_to_python(self, node):
        return str(node.name)

class JSONConfList(list):
    def __init__(self, arglist=[]):
        super().__init__()
        self.extend(arglist)
    def extend(self, other):
        for elem in other:
            if isinstance(elem, dict):
                self.append(JSONConfDict(elem))
            elif isinstance(elem, list):
                self.append(JSONConfList(elem))
            else:
                self.append(elem)

class JSONConfDict(dict):
    def __init__(self, argdict={}):
        super().__init__()
        self.update(argdict)
        self.__dict__ = self
    def update(self, other):
        for key, value in other.items():
            # Merge existing entry or add a new one
            if key in self:
                if isinstance(self[key], JSONConfList):
                    self[key].extend(value)
                elif isinstance(self[key], JSONConfDict):
                    self[key].update(value)
                else:
                    self[key] = value
            else:
                if isinstance(value, dict):
                    self[key] = JSONConfDict(value)
                elif isinstance(value, list):
                    self[key] = JSONConfList(value)
                else:
                    self[key] = value

def json5_read(file_path, error_exit=True):
    with open(file_path, 'r') as file:
        try:
            return JSONConfDict(json5.loads(file.read(), loader=JSONCompatLoader()))
        except ValueError as e:
            raise InvalidJSONError(str(e), file_path)

def json5_write(jsondict, file_path):
    with open(file_path, 'w') as file:
        file.write(json5.dumps(jsondict))
