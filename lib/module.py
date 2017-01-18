from converter import Converter
from util import Util

import copy
import csv
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

from collections import OrderedDict

# ac: algorithmic circuit
class Module:
    dump_directory_path = '.'
    file_name_prefix    = 'module_'
    inner_margin        = [2, 2, 2]
    ac_margin           = [0, 2, 0]
    cnot_length         = 4
    pin_length          = 6

    __counter  = {}
    __commands = {
        'optimization'   : './bin/optimization/sa %s',
        'placement'      : './bin/placement/spp3 %s',
        'parallelization': './bin/parallelization/csvd_ev1 %s'
    }

    @classmethod
    def make_id(cls, type_name):
        number = cls.__counter.get(type_name, 0)
        cls.__counter[type_name] = number + 1
        return type_name.lower() + '_' + str(number)

    @classmethod
    @Util.decode_dagger
    def make_file_name(cls, id):
        return cls.dump_directory_path + '/' + cls.file_name_prefix + id + '.json'

    @classmethod
    def __exec_subproccess(cls, command_key, file_name):
        command = cls.__commands[command_key] % (file_name)
        try:
            stdout = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print('Subprocess output:', os.linesep, e.output, os.linesep, file=sys.stderr)
            raise
        return stdout.decode('utf-8')

    def __init__(self, template, inners, *constraints):
        self.id         = self.make_id(template.type_name)
        self.type_name  = template.type_name
        self.circuit    = template.circuit
        self.error_rate = template.pure_error_rate
        self.size       = template.size # 後に更新 (elementary module用)
        self.inners     = inners

        self.__prepare()

        self.__parallelize()
        self.__place(*constraints)
        self.__connect()

        # テスト用
        self.__set_size()

    def dump(self, indent=4):
        if not os.path.isdir(self.dump_directory_path):
            os.makedirs(self.dump_directory_path)

        file_name = self.make_file_name(self.id)
        with open(file_name, 'w') as fp:
            json.dump(self.to_output_format(), fp, indent=indent)
            fp.flush()

    def to_output_format(self):
        return OrderedDict((
            ('id'     , self.id),
            ('type'   , self.type_name),
            ('size'   , self.size),
            ('error'  , self.error_rate),
            ('circuit', self.circuit),
            ('modules', self.to_output_format_inners())
        ))

    def to_output_format_inners(self):
        output_format = []
        for inner in self.inners:
            output_format.extend(inner.to_output_format())
        return output_format

    def to_icpm(self):
        return OrderedDict((
            ('format' , 'icpm'),
            ('circuit', self.circuit)
        ))

    def to_qc(self):
        return Converter.to_qc(self.to_icpm())

    def get_inner(self, inner_id):
        return self.inners[self.__inner_id_dict[inner_id]]

    def is_elementary(self):
        return len(self.inners) == 0

    def __prepare(self):
        self.__set_inner_id_dict()
        self.__set_ac_size()

    def __set_inner_id_dict(self):
        self.__inner_id_dict = {inner.id: i for i, inner in enumerate(self.inners)}

    def __set_ac_size(self):
        # i番目のビット線の座標は [(i + 1) * 2, 0, 0] (i >= 0)
        w = (len(self.circuit['bits']) + 1) << 1
        d = self.__calculate_ac_length()
        self.__ac_size = [w, 2, d]

    def __calculate_ac_length(self):
        circuit_length = 0
        for operation_step in self.circuit['operations']:
            if not isinstance(operation_step, list):
                operation_step = [operation_step]

            step_length = 0
            for operation in operation_step:
                operation_type = operation['type'].lower()
                if operation_type == 'cnot':
                    step_length = max(step_length, self.cnot_length)
                elif operation_type == 'pin':
                    step_length = max(step_length, self.pin_length)

            circuit_length += step_length
        return circuit_length

    # TODO: connectionを考慮
    @Util.non_elementary()
    def __set_size(self):
        ac = {'size': self.__ac_size, 'position': [0, 0, 0]}
        rectangles = self.to_output_format_inners() + [ac]
        convex_hull = self.__calculate_convex_hull(rectangles)
        self.size = convex_hull['size']
        self.__update_positions(convex_hull['position'])

    def __update_positions(self, base_position):
        self.__update_inners_position(base_position)
        #self.__update_connections_position(base_position)

    def __update_inners_position(self, base_position):
        for i, inner in enumerate(self.inners):
            for j in range(len(inner.positions)):
                for k in range(3):
                    self.inners[i].positions[j][k] += base_position[k]

    def __parallelize(self):
        with tempfile.NamedTemporaryFile('w') as fp:
            json.dump(self.to_qc(), fp)
            fp.flush()
            result = self.__exec_subproccess('parallelization', fp.name)

        icpm = Converter.to_icpm(json.loads(result))
        self.circuit['operations'] = icpm.get('circuit', {}).get('operations', [])

        #self.set_bits()

    def __place(self, permissible_error_rate, permissible_size):
        self.__set_id_of_pins()
        self.__set_spares(permissible_error_rate)
        self.__place_inners(permissible_size)

    # 同一テンプレートから異なるモジュールを生成しない場合
    def __set_id_of_pins(self):
        inner_type_dict = {inner.type_name: inner.id for inner in self.inners}

        def convert(elements):
            for i in range(len(elements)):
                if isinstance(elements[i], list):
                    convert(elements[i])
                    continue
                if elements[i]['type'] != 'pin' : continue
                type_name = elements[i]['module']
                elements[i]['module'] = inner_type_dict[type_name]

        for key in ['initializations', 'operations']:
            convert(self.circuit[key])

    @Util.non_elementary()
    def __set_spares(self, permissible_error_rate):
        self.__optimize_spare_counts(permissible_error_rate)
        self.__update_error_rate()

    def __optimize_spare_counts(self, permissible_error_rate):
        modules = self.__make_optimization_modules()

        with tempfile.NamedTemporaryFile('w') as fp:
            json.dump({
                'modules'        : modules,
                'error_threshold': permissible_error_rate
            }, fp)

            fp.flush()
            result = self.__exec_subproccess('optimization', fp.name)

        spare_counts = list(map(int, result.rstrip().split(',')))

        return self.__set_spare_counts(spare_counts)

    def __make_optimization_modules(self):
        return [inner.to_optimization_format() for inner in self.inners]

    def __set_spare_counts(self, spare_counts):
        for inner, spare_count in zip(self.inners, spare_counts):
            inner.spare_count = spare_count

    def __update_error_rate(self):
        self.error_rate = 1.0 - np.prod([
            self.__calculate_inner_success_rate(inner) for inner in self.inners
        ])

    def __calculate_inner_success_rate(self, inner):
        e, n, x = inner.error_rate, inner.count, inner.spare_count
        return math.fsum([
            Util.combination(n + x, n + i) * pow(e, x - i) * pow(1.0 - e, n + i)
            for i in range(x + 1)
        ])

    @Util.non_elementary()
    def __place_inners(self, permissible_size):
        max_inner_size = self.__max_inner_size()
        rectangles, inner_ids = self.__make_placement_rectangles()

        # マージンを考慮
        max_inner_size = [max_inner_size[i] + self.inner_margin[i] * 2 for i in range(3)]
        ac_size        = [self.__ac_size[i] + self.ac_margin[i]        for i in range(3)]

        # Y軸方向のストリップパッキング
        base = self.__make_placement_base_y(max_inner_size, ac_size)
        rectangles = self.__place_rectangles(rectangles, base)

        if not self.__is_within_permissible_size(rectangles, permissible_size):
            # Z軸方向のストリップパッキング
            base = self.__make_placement_base_z(max_inner_size, ac_size, permissible_size)
            rectangles = self.__place_rectangles(rectangles, base)

        self.__set_inners_positions(rectangles, inner_ids)

    def __place_rectangles(self, rectangles, base):
        with tempfile.NamedTemporaryFile('w') as fp:
            json.dump({
                'hyperrectangles': rectangles,
                'base'           : base
            }, fp)

            fp.flush()
            result = self.__exec_subproccess('placement', fp.name)

        return json.loads(result)['hyperrectangles']

    def __is_within_permissible_size(self, rectangles, permissible_size):
        convex_hull = self.__calculate_convex_hull(rectangles)

        if convex_hull['size'][0] > permissible_size[0]:
            return False
        if convex_hull['size'][1] > permissible_size[1] - \
           (self.__ac_size[1] + self.ac_margin[1]):
            return False

        return True

    def __calculate_convex_hull(self, rectangles):
        position            = [ sys.maxsize for i in range(3)]
        antigoglin_position = [-sys.maxsize for i in range(3)]

        for rectangle in rectangles:
            size = rectangle['size']
            for i in range(3):
                n = rectangle['position'][i]
                position[i]            = min(position[i], n)
                antigoglin_position[i] = max(antigoglin_position[i], size[i] + n)

        size = [antigoglin_position[i] - position[i] for i in range(3)]
        return {
            'size'    : size,
            'position': position
        }

    def __make_placement_rectangles(self):
        rectangles = []
        inner_ids = []

        for inner in self.inners:
            size =  [inner.size[i] + self.inner_margin[i] * 2 for i in range(3)]
            rectangle = {'size': size}
            for i in range(inner.count + inner.spare_count):
                rectangles.append(rectangle)
                inner_ids.append(inner.id)

        return rectangles, inner_ids

    def __make_placement_base_y(self, max_inner_size, ac_size):
        x = max(ac_size[0], max_inner_size[0])
        z = max(ac_size[2], max_inner_size[2])
        base_size = [x, 0, z]
        base_position = [0, ac_size[1], 0]
        return {
            'size'    : base_size,
            'position': base_position
        }

    def __make_placement_base_z(self, max_inner_size, ac_size, permissible_size):
        x = max(ac_size[0], max_inner_size[0])
        y = permissible_size[1] - ac_size[1]
        base_size = [x, y, 0]
        base_position = [0, ac_size[1], 0]
        return {
            'size'    : base_size,
            'position': base_position
        }

    def __max_inner_size(self):
        max_inner_size = [0, 0, 0]
        for inner in self.inners:
            for i in range(3):
                max_inner_size[i] = max(max_inner_size[i], inner.size[i])
        return max_inner_size

    def __set_inners_positions(self, rectangles, inner_ids):
        for rectangle, id in zip(rectangles, inner_ids):
            self.get_inner(id).positions.append([
                rectangle['position'][i] + self.inner_margin[i]
                for i in range(3)
            ])

    def __set_bits(self):
        # テスト
        #x = self.get_time_axis_direction_length()
        x = 10

        for (index, bit) in enumerate(self.circuit.bits):
            self.circuit.bits[index] = {
                'id'   : index,
                'range': [0, x]
                #'source'     : [[0, index, 0], [0, index, 1]],
                #'destination': [[x, index, 0], [x, index, 1]]
            }

    def __connect(self):
        cmd = './bin/connection'
        pass
