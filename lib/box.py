from elements import Elements
from inner_module import InnerModule
from module import Module
from util import Util

import json
import sympy

from functools import reduce

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
            fp = open(file_name, 'r')
        except IOError:
            # ゲート変換データベースによる分解
            #cls.decompose()
            pass

        raw = json.load(fp)
        fp.close()

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
        pure_success_rate = 1.0 - self.pure_error_rate

        for raw_inner in raw_inners:
            inner_type = raw_inner.get('type')
            inner_count = raw_inner.get('number', 1)

            if not inner_type:
                continue

            inner = Box.get(inner_type)
            self.inners.append((inner, inner_count))
            pure_success_rate *= pow(1.0 - inner.pure_error_rate, inner_count)

        self.pure_error_rate = 1.0 - pure_success_rate

    def deploy(self, permissible_error_rate, permissible_size):
        inner_module = self.deploy_from_cache(permissible_error_rate, permissible_size)

        if inner_module:
            return inner_module

        inner_modules = self.deploy_inners(permissible_error_rate, permissible_size)
        module = Module(self, inner_modules, permissible_error_rate, permissible_size)
        module.dump()
        self.cache_module_id(module.id, permissible_error_rate, permissible_size)
        inner_module = InnerModule(module)

        return inner_module

    def deploy_from_cache(self, permissible_error_rate, permissible_size):
        key = (self.type_name, permissible_error_rate, permissible_size)
        module_id = Box.deployment_cache.get(key)
        inner_module = InnerModule.load(module_id)

        return inner_module

    def deploy_inners(self, permissible_error_rate, permissible_size):
        inner_modules = {}

        if self.is_elementary():
            return inner_modules

        inner_args_func = self.create_inner_deployment_args_func(permissible_error_rate, \
                                                                 permissible_size)

        for (inner, inner_count) in self.inners:
            (inner_permissible_error_rate, inner_permissible_size) = inner_args_func(inner)

            for i in range(inner_count):
                inner_module = inner.deploy(inner_permissible_error_rate, \
                                            inner_permissible_size)

                if inner_module.id in inner_modules:
                    inner_modules[inner_module.id].count += 1
                else:
                    inner_modules[inner_module.id] = inner_module

        self.inners.clear()

        return inner_modules

    def create_inner_deployment_args_func(self, permissible_error_rate, permissible_size):
        assert(not self.is_elementary())

        error_rate_func = self.create_permissible_error_rate_func(permissible_error_rate)

        def inner_deployment_args_func(inner):
            if inner.is_elementary():
                return (inner.pure_error_rate, permissible_size)

            inner_permissible_error_rate = error_rate_func(inner.pure_error_rate)
            # テスト
            inner_permissible_size = permissible_size

            return (inner_permissible_error_rate, inner_permissible_size)

        return inner_deployment_args_func

    def create_permissible_error_rate_func(self, permissible_error_rate):
        # ニュートン法における許容誤差
        e = 0.00001

        (m, x) = sympy.symbols('m x')
        f = -m * x + 1

        g = 1
        for (inner, inner_count) in self.inners:
            g *= f.subs([(x, inner.pure_error_rate)]) ** inner_count
        g -= 1 - permissible_error_rate

        m0 = Util.newton_raphson_method(g, m, e, lambda e, y: y < 0 or y > e)
        h = 1 - f.subs([(m, m0)])

        return lambda xi: float(h.subs([(x, xi)]))

    def cache_module_id(self, module_id, permissible_error_rate, permissible_size):
        key = (self.type_name, permissible_error_rate, permissible_size)
        Box.deployment_cache[key] = module_id

    def is_elementary(self):
        return not self.inners
