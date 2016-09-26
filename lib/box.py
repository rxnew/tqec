from elements import Elements
from module import Module

import json

class Box:
    cache = {}
    data_directory_path = './data/box/'

    @classmethod
    def get(cls, type_name):
        if type_name in cls.cache:
            return cls.cache[type_name]

        box = Box(type_name)
        cls.cache[type_name] = box

        return box

    def __new__(cls, type_name):
        if not type_name:
            return None
        return super().__new__(cls)

    def __init__(self, type_name):
        raw = self.get_raw(type_name)

        self.type_name = type_name
        self.pure_error_rate = raw.get('error', 0.0)
        self.elements = Elements(raw.get('elements', {}))
        self.inners = []

        self.set_inners(raw.get('elements', {}).get('boxes', []))

    def get_raw(self, type_name):
        f = open(Box.data_directory_path + type_name.lower() + '.json')
        raw = json.load(f)
        f.close()

        return raw

    def set_inners(self, raw_inners):
        pure_success_rate = 1 - self.pure_error_rate

        for raw_inner in raw_inners:
            inner_type = raw_inner.get('type')
            inner_number = raw_inner.get('number', 1)

            if not inner_type:
                continue

            inner = Box.get(inner_type)
            self.inners.append((inner, inner_number))

            pure_success_rate *= 1 - inner.pure_error_rate

        self.pure_error_rate = 1 - pure_success_rate

    def deploy(self, permissible_error_rate, permissible_size):
        inner_modules = []

        for (inner, number) in self.inners:
            inner_permissible_error_rate = 0.4
            inner_permissible_size = [10, 30]
            for i in range(number):
                inner_module = inner.deploy(inner_permissible_error_rate, inner_permissible_size)
                inner_modules.append(inner_module)

        self.inners.clear()

        module = Module(self, inner_modules, permissible_error_rate, permissible_size)
        module.dump()

        return module

class FormatError(Exception):
    def __init__(self, message):
        self.message = message
