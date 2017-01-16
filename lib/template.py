from inner_module import InnerModule
from module import Module
from converter import Converter
from util import Util

import json
import logging
import sympy

from collections import OrderedDict
from functools import reduce

class Template:
    data_directory_path = './data/templates/'
    __module_count = 0

    @classmethod
    @Util.encode_dagger
    @Util.cache()
    def get_instance(cls, type_name):
        return cls(type_name)

    @classmethod
    @Util.decode_dagger
    def load(cls, type_name):
        file_name = cls.data_directory_path + type_name.lower() + '.json'

        try:
            fp = open(file_name, 'r')
        except IOError:
            # ゲート変換データベースによる分解
            #cls.decompose()
            pass

        json_object = json.load(fp, object_pairs_hook=OrderedDict)
        Converter.complement_icpm(json_object)
        fp.close()

        return json_object

    def __init__(self, type_name):
        json_object = self.load(type_name)
        self.type_name       = type_name
        self.pure_error_rate = json_object.get('error', 0.0)
        self.size            = json_object.get('size')
        self.circuit         = json_object.get('circuit', {})
        self.inners          = [] # (inner, count)
        self.__set_inners(self.__collect_inners())

    def deploy(self, permissible_error_rate, permissible_size):
        return self.__deploy(self.type_name, permissible_error_rate, permissible_size)

    def is_elementary(self):
        return not self.inners

    @Util.cache(encoder=InnerModule.load, decoder=lambda arg: arg.id,
                keygen=lambda args:
                (args[0], Util.significant_figure(args[1], 2), args[2]))
    def __deploy(self, type_name, *constraints):
        inner_modules = self.__deploy_inners(*constraints)
        module = Module(self, inner_modules, *constraints)
        module.dump()
        logging.info('Completed to dump the module "%s"', module.id)
        return InnerModule(module)

    def __collect_inners(self):
        initializations = self.circuit['initializations']
        operations = self.circuit['operations']
        counts = OrderedDict()

        for elements in [initializations, operations]:
            for element in elements:
                if element['type'] == 'pin':
                    module = element['module']
                    counts[module] = counts.get(module, 0) + 1

        return [{'type': key, 'number': value} for key, value in counts.items()]

    def __set_inners(self, inners):
        pure_success_rate = 1.0 - self.pure_error_rate

        for inner in inners:
            inner_type = inner['type']
            inner_count = inner['number']
            inner = self.get_instance(inner_type)
            self.inners.append((inner, inner_count))
            pure_success_rate *= pow(1.0 - inner.pure_error_rate, inner_count)

        self.pure_error_rate = 1.0 - pure_success_rate

    # 同一テンプレートから異なるモジュールを生成しない場合
    @Util.non_elementary([])
    def __deploy_inners(self, *constraints):
        inner_modules = []
        inner_args_func = self.__make_deployment_args_func(*constraints)

        for inner, inner_count in self.inners:
            inner_constraints = inner_args_func(inner)
            inner_module = inner.deploy(*inner_constraints)
            inner_module.count = inner_count
            inner_modules.append(inner_module)

        self.inners.clear()
        return inner_modules

    # 同一テンプレートから異なるモジュールを生成する可能性がある場合 (現在不使用)
    @Util.non_elementary([])
    def __deploy_inners_not_used(self, *constraints):
        inner_modules_dict = {}
        inner_args_func = self.__make_deployment_args_func(*constraints)

        for inner, inner_count in self.inners:
            inner_constraints = inner_args_func(inner)

            for i in range(inner_count):
                inner_module = inner.deploy(*inner_constraints)
                if inner_module.id in inner_modules_dict:
                    inner_modules_dict[inner_module.id].count += 1
                else:
                    inner_modules_dict[inner_module.id] = inner_module

        self.inners.clear()
        return list(inner_modules_dict.values())

    def __make_deployment_args_func(self, permissible_error_rate, permissible_size):
        error_rate_func = self.__make_permissible_error_rate_func(permissible_error_rate)

        def make_deployment_args(inner):
            if inner.is_elementary():
                return inner.pure_error_rate, permissible_size

            inner_permissible_error_rate = error_rate_func(inner.pure_error_rate)
            # Y軸方向はアルゴリズミック回路の分だけ引く
            inner_permissible_size = (
                permissible_size[0],
                permissible_size[1] - (2 + Module.ac_margin[1])
            )

            return inner_permissible_error_rate, inner_permissible_size

        return make_deployment_args

    def __make_permissible_error_rate_func(self, permissible_error_rate):
        # ニュートン法における許容誤差
        e = 0.00001

        m, x = sympy.symbols('m x')
        f = -m * x + 1

        g = 1
        for inner, inner_count in self.inners:
            g *= f.subs([(x, inner.pure_error_rate)]) ** inner_count
        g -= 1 - permissible_error_rate

        m0 = Util.newton_raphson_method(g, m, e, lambda e, y: y < 0 or y > e)
        h = 1 - f.subs([(m, m0)])

        return lambda xi: float(h.subs([(x, xi)]))
