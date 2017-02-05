from switch_module import SwitchModule
from converter import Converter
from util import Util

import csv
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

from collections import OrderedDict, defaultdict

# ac: algorithmic circuit
class Module:
    dump_directory_path = '.'
    file_name_prefix    = 'module_'
    inner_margin        = [2, 2, 2]
    ac_margin           = [0, 2, 0]
    cnot_length         = 4
    pin_length          = 6
    pin_margin          = 2

    __counter  = {}
    __commands = {
        'optimization'   : './bin/optimization/sa %s',
        'placement'      : './bin/placement/spp3 %s',
        'parallelization': './bin/parallelization/csvd_ev1 %s',
        'connection'     : './bin/connection/connection %s'
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
        self.geometry   = template.geometry
        self.error_rate = template.pure_error_rate
        self.size       = template.size # 後に更新 (elementary module用)
        self.inners     = inners

        if self.is_regular(): self.__init_regular(*constraints)
        else                : self.__init_non_regular()

    def dump(self, indent=4):
        if not os.path.isdir(self.dump_directory_path):
            os.makedirs(self.dump_directory_path)

        file_name = self.make_file_name(self.id)
        with open(file_name, 'w') as fp:
            json.dump(self.to_output_format(), fp, indent=indent)
            fp.flush()

    def to_output_format(self):
        return OrderedDict((
            ('type'    , 'tqec'),
            ('id'      , self.id),
            ('type'    , self.type_name),
            ('size'    , self.size),
            ('error'   , self.error_rate),
            ('circuit' , self.circuit),
            ('geometry', self.geometry)
        ))

    def to_output_format_inners(self):
        output_format = []
        for inner in self.inners + self.switches:
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

    def get_switch(self, switch_id):
        return self.switches[self.__switch_id_dict[switch_id]]

    def is_elementary(self):
        return len(self.inners) == 0

    def is_regular(self):
        return self.geometry == None

    def __init_regular(self, *constraints):
        self.__prepare()

        self.__parallelize()
        self.__place(*constraints)
        self.__connect()

        # テスト用
        self.__set_size()
        self.__set_geometry()

    def __init_non_regular(self):
        self.geometry['inputs']  = self.geometry.get('inputs' , [])
        self.geometry['outputs'] = self.geometry.get('outputs', [])

    def __prepare(self):
        self.__set_inner_id_dict()
        self.__set_ac_size()

    def __set_inner_id_dict(self):
        self.__inner_id_dict = {inner.id: i for i, inner in enumerate(self.inners)}

    def __set_switch_id_dict(self, switches):
        self.switches = []
        self.__switch_id_dict = {}
        for switch in switches:
            if switch.id in self.__switch_id_dict:
                self.switch[self.__switch_id_dict[switch.id]].count += 1
                continue
            self.__switch_id_dict[switch.id] = len(self.switches)
            self.switches.append(switch)

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
                    step_length = max(step_length, self.pin_length + self.pin_margin)

            circuit_length += step_length
        return circuit_length

    # TODO: connectionを考慮
    # TODO: -1の位置のCNOTの扱い
    def __set_size(self):
        ac = {'size': self.__ac_size, 'position': [0, 0, 0]}
        rectangles = self.to_output_format_inners() + [ac]
        convex_hull = self.__calculate_convex_hull(rectangles)
        self.size = convex_hull['size']
        self.__update_positions(convex_hull['position'])

    def __set_geometry(self):
        self.geometry = Converter.icpm_to_tqec(self.circuit)
        self.geometry['logical_qubits'].extend(self.__make_geometry_connections())
        self.geometry['modules'] = self.to_output_format_inners()
        self.geometry['inputs']  = self.__make_geometry_inputs()
        self.geometry['outputs'] = self.__make_geometry_outpus()

    def __make_geometry_connections(self):
        logical_qubits = []
        id_count = self.__find_logical_qubits_max_id(self.geometry['logical_qubits'])
        for connection in self.__connections:
            # 接続に失敗した経路を無視 (暫定)
            if len(connection) == 0: continue
            id_count += 1
            logical_qubits.append(OrderedDict((
                ('id'    , id_count),
                ('type'  , 'rough'),
                ('blocks', [connection])
            )))
        return logical_qubits

    def __find_logical_qubits_max_id(self, logical_qubits):
        max_id = 0
        for logical_qubit in logical_qubits:
            max_id = max(max_id, logical_qubit['id'])
        return max_id

    def __make_geometry_inputs(self):
        inputs = []
        for bit in self.circuit['inputs']:
            x = bit << 1
            inputs.append(OrderedDict((
                ('id'       , bit),
                ('positions', [[x, 0, 0], [x, 2, 0]])
            )))
        return inputs

    def __make_geometry_outpus(self):
        outputs = []
        for bit in self.circuit['outputs']:
            x = bit << 1
            z = self.size[2]
            outputs.append(OrderedDict((
                ('id'       , bit),
                ('positions', [[x, 0, z], [x, 2, z]])
            )))
        return outputs

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

    def __place(self, permissible_error_rate, permissible_size):
        self.__set_id_of_pins()
        self.__set_spares(permissible_error_rate)
        self.__set_switches()
        self.__place_inners(permissible_size)
        self.__place_switches(permissible_size)

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
        self.__set_spare_counts(spare_counts)

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

    def __set_switches(self):
        switch_io_counts = defaultdict(lambda: defaultdict(int))
        for inner in self.inners:
            if inner.spare_count == 0: continue
            switch_io_counts[inner.type_name]['input']  += inner.spare_count + inner.count
            switch_io_counts[inner.type_name]['output'] += inner.count
        self.__set_switch_id_dict([
            SwitchModule(type_name, io_count['input'], io_count['output'])
            for type_name, io_count in switch_io_counts.items()
        ])

    @Util.non_elementary()
    def __place_inners(self, permissible_size):
        max_inner_size = self.__max_inner_size()
        max_inner_size = [max_inner_size[i] + self.inner_margin[i] * 2 for i in range(3)]
        rectangles, inner_ids = self.__make_placement_rectangles(self.inners)

        # Y軸方向のストリップパッキング
        base = self.__make_placement_base_y(max_inner_size)
        rectangles = self.__place_rectangles(rectangles, base)

        if not self.__is_within_permissible_size(rectangles, permissible_size):
            # Z軸方向のストリップパッキング
            base = self.__make_placement_base_z(permissible_size)
            rectangles = self.__place_rectangles(rectangles, base)

        self.__set_inners_positions(rectangles, inner_ids, self.get_inner)

    @Util.non_elementary()
    def __place_switches(self, permissible_size):
        rectangles, inner_ids = self.__make_placement_rectangles(self.switches)
        base = self.__make_placement_base_switch(permissible_size) 
        rectangles = self.__place_rectangles(rectangles, base)
        self.__set_inners_positions(rectangles, inner_ids, self.get_switch)

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

    def __make_placement_rectangles(self, inners):
        rectangles = []
        inner_ids = []

        for inner in inners:
            size =  [inner.size[i] + self.inner_margin[i] * 2 for i in range(3)]
            rectangle = {'size': size}
            for i in range(inner.count + inner.spare_count):
                rectangles.append(rectangle)
                inner_ids.append(inner.id)

        return rectangles, inner_ids

    def __make_placement_base_y(self, max_inner_size):
        ac_size = Util.vector_add(self.__ac_size, self.ac_margin)
        x = max(ac_size[0], max_inner_size[0])
        z = max(ac_size[2], max_inner_size[2])
        base_size = [x, 0, z]
        base_position = [0, ac_size[1], 0]
        return {
            'size'    : base_size,
            'position': base_position
        }

    def __make_placement_base_z(self, permissible_size):
        ac_size = Util.vector_add(self.__ac_size, self.ac_margin)
        #x = max(ac_size[0], max_inner_size[0])
        x = permissible_size[0] - ac_size[0]
        y = permissible_size[1] - ac_size[1]
        base_size = [x, y, 0]
        base_position = [0, ac_size[1], 0]
        return {
            'size'    : base_size,
            'position': base_position
        }

    def __make_placement_base_switch(self, permissible_size):
        base = self.__make_placement_base_z(permissible_size)
        base_z = 0
        for inner in self.inners:
            for position in inner.positions:
                base_z = max(base_z, position[2] + inner.size[2])
        base['position'][2] = base_z + (self.inner_margin[2] << 1)
        return base

    def __max_inner_size(self):
        max_inner_size = [0, 0, 0]
        for inner in self.inners:
            for i in range(3):
                max_inner_size[i] = max(max_inner_size[i], inner.size[i])
        return max_inner_size

    def __set_inners_positions(self, rectangles, inner_ids, inner_getter):
        for rectangle, id in zip(rectangles, inner_ids):
            inner_getter(id).positions.append([
                #rectangle['position'][i] + self.inner_margin[i]
                rectangle['position'][i] + (self.inner_margin[i] if i == 1 else 0)
                for i in range(3)
            ])

    def __connect(self):
        endpoints = self.__scale_down(self.__make_connection_endpoints())
        obstacles = self.__scale_down(self.__make_connection_obstacles())
        region    = self.__scale_down(self.__make_connection_region())

        with tempfile.NamedTemporaryFile('w') as fp:
            json.dump({
                'endpoints': endpoints,
                'obstacles': obstacles,
                'region'   : region
            }, fp)

            fp.flush()
            result = self.__exec_subproccess('connection', fp.name)

        #print(result)
        self.__connections = self.__scale_up(json.loads(result)['connections'])

    def __make_connection_endpoints(self):
        pins = defaultdict(list)
        inner_pins = defaultdict(list)

        for initialization in self.circuit['initializations']:
            if initialization['type'] != 'pin': continue
            x = initialization['bit'] << 1
            for i in range(2):
                pins[initialization['module']].append([x, i << 1, 0])

        for step, operation_step in enumerate(self.circuit['operations']):
            if not isinstance(operation_step, list):
                operation_step = [operation_step]
            step_z = step * self.pin_length + self.pin_margin
            z = [step_z, step_z + self.pin_length]
            for operation in operation_step:
                if operation['type'].lower() != 'pin': continue
                bits = operation['controls'] + operation['targets']
                for i in range(2):
                    for bit in bits:
                        x = bit << 1
                        for j in range(2):
                            pins[operation['module']].append([x, j << 1, z[i]])

        for inner in self.inners:
            ios = inner.inputs + inner.outputs
            for base_position in inner.positions:
                for io in ios:
                    for i in range(2):
                        position = Util.vector_add(base_position, io['positions'][i])
                        inner_pins[inner.id].append(position)

        endpoints = []

        for type_name in pins.keys():
            for i in range(len(pins[type_name])):
                endpoints.append([pins[type_name][i], inner_pins[type_name][i]])

        return endpoints

    def __make_connection_obstacles(self):
        obstacles = [{'size': self.__ac_size, 'position': [0, 0, 0]}]
        for inner in self.inners + self.switches:
            for position in inner.positions:
                obstacles.append({'size': inner.size, 'position': position})
        return obstacles

    def __make_connection_region(self):
        # TODO: 許容サイズを考慮する
        # self.__set_sizeと処理が被る
        ac = {'size': self.__ac_size, 'position': [0, 0, 0]}
        rectangles = self.to_output_format_inners() + [ac]
        convex_hull = self.__calculate_convex_hull(rectangles)
        size = Util.vector_add(convex_hull['size'], [4, 4, 20])
        position = Util.vector_add(convex_hull['position'], [-2, -2, -10])
        return {'size': size, 'position': position}

    def __scale(self, element, scaling):
        if isinstance(element, int):
            return scaling(element)
        if isinstance(element, list):
            scaled_element = []
            for i in range(len(element)):
                scaled_element.append(self.__scale(element[i], scaling))
        elif isinstance(element, dict):
            scaled_element = {}
            for key in element.keys():
                scaled_element[key] = self.__scale(element[key], scaling)
        return scaled_element

    def __scale_up(self, element, factor=1):
        return self.__scale(element, lambda x: x << factor)

    def __scale_down(self, element, factor=1):
        return self.__scale(element, lambda x: x >> factor)
