from module import Module

from collections import defaultdict
from elements import Elements

import json

class Box:
    data_directory_path = './data/box/'
    cache = {}
    deployment_cache = {}

    @classmethod
    def get(cls, type_name):
        if type_name in cls.cache:
            return cls.cache[type_name]

        box = Box(type_name)
        cls.cache[type_name] = box

        return box

    @classmethod
    def get_raw(cls, type_name):
        file_name = cls.data_directory_path + type_name.lower() + '.json'

        try:
            f = open(file_name, 'r')
        except IOError:
            # ゲート変換データベースによる分解
            #cls.decompose()
            pass

        raw = json.load(f)
        f.close()

        return raw

    def __new__(cls, type_name):
        if not type_name:
            return None
        return super().__new__(cls)

    def __init__(self, type_name):
        raw = Box.get_raw(type_name)

        self.type_name = type_name
        self.pure_error_rate = raw.get('error', 0.0)
        self.elements = Elements(raw.get('elements', {}))
        self.inners = []

        self.set_inners(raw.get('elements', {}).get('boxes', []))

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
        #raw_module = self.deploy_from_cache(permissible_error_rate, permissible_size)
        #if raw_module:
        #    return raw_module
        module_value = self.deploy_from_cache(permissible_error_rate, permissible_size)
        if module_value[0]:
            return module_value

        #raw_inner_modules = []
        raw_inner_modules = {}

        for (inner, number) in self.inners:
            # テスト
            inner_permissible_error_rate = 0.4
            inner_permissible_size = (10, 30)
            for i in range(number):
                #raw_inner_module = inner.deploy(inner_permissible_error_rate, \
                #                                inner_permissible_size)
                #raw_inner_modules.append(raw_inner_module)
                (inner_module_id, raw_inner_module) \
                    = inner.deploy(inner_permissible_error_rate, inner_permissible_size)
                if inner_module_id in raw_inner_modules:
                    raw_inner_modules[inner_module_id]['number'] += 1
                else:
                    raw_inner_modules[inner_module_id] = raw_inner_module

        self.inners.clear()

        module = Module(self, raw_inner_modules, permissible_error_rate, permissible_size)
        module.dump()

        raw_module = module.get_raw_inner_format()
        raw_module['number'] = 1

        return (module.id, raw_module)

    # まだキャッシュへの保存は実装していない
    def deploy_from_cache(self, permissible_error_rate, permissible_size):
        key = (self.type_name, permissible_error_rate, permissible_size)
        module_id = Box.deployment_cache.get(key)
        raw_module = Module.load_raw_inner_format(module_id, self.type_name)

        return (module_id, raw_module)

class FormatError(Exception):
    def __init__(self, message):
        self.message = message
