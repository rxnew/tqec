from module import Module

import json

class Box:
    cache = {}

    @classmethod
    def get(cls, type_name):
        if type_name in cls.cache:
            return cls.cache[type_name]

        f = open('data/box/' + type_name.lower() + '.json')
        raw = json.load(f)
        f.close()

        cls.cache[type_name] = raw

        return raw

    def __new__(cls, type_name):
        if not type_name:
            return None
        return super().__new__(cls)

    def __init__(self, type_name):
        raw = Box.get(type_name)

        self.type_name = type_name
        self.elements = raw.get('elements', {})
        self.pure_error_rate = raw.get('error', 0.0)
        self.inners = []

        self.check_formats()
        self.collect_formats()
        self.set_inners()

    def check_formats(self):
        if not isinstance(self.elements, dict):
            raise FormatError('Elements is not a dict object.')

        if not isinstance(self.pure_error_rate, float) and \
           not isinstance(self.pure_error_rate, int):
            raise FormatError('A pure error rate is not a float or int object.')

    def collect_formats(self):
        keys = ['bits',
                'inputs',
                'outputs',
                'initializations',
                'measurements',
                'operations',
                'boxes']

        for key in keys:
            if not key in self.elements:
                self.elements[key] = []

    def set_inners(self):
        pure_success_rate = 1 - self.pure_error_rate

        for raw_inner in self.elements.get('boxes', []):
            inner_type = raw_inner.get('type')
            inner_number = raw_inner.get('number', 1)

            if not inner_type:
                continue

            inner = Box(inner_type)
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

        module = Module(self, inner_modules, permissible_error_rate, permissible_size)

        return module

class FormatError(Exception):
    def __init__(self, message):
        self.message = message
