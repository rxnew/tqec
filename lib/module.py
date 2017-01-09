from converter import Converter
from util import Util

import copy
import csv
import json
import os
import re
import subprocess
import tempfile

from collections import OrderedDict
from functools import reduce

class Module:
    dump_directory_path = './'
    counter = {}
    commands = {
        'spare_optimization': './c++/bin/spare_optimization %s %f',
        'inners_placement'  : './optimizations/module_placement/bin/spp3 %s',
        'parallelization'   : './optimizations/algorithmic_circuit_steps/bin/main %s'
    }

    @classmethod
    def make_id(cls, type_name):
        number = cls.counter.get(type_name, 0)
        cls.counter[type_name] = number + 1

        return type_name.lower() + '_' + str(number)

    @classmethod
    def make_file_name(cls, id):
        return cls.dump_directory_path + 'module_' + id + '.json'

    @classmethod
    def __exec_subproccess(cls, command_key, file_name):
        command = Module.commands[command_key] % (file_name)
        process = subprocess.Popen(command, shell=True, \
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        stdout = process.communicate()[0]
        return stdout.decode('utf-8')

    def __init__(self, template, inners, permissible_error_rate, permissible_size):
        self.id         = self.make_id(template.type_name)
        self.type_name  = template.type_name
        self.circuit    = template.circuit
        self.error_rate = template.pure_error_rate
        self.inners     = inners

        self.__prepare()

        self.__parallelize()
        self.__place(permissible_error_rate, permissible_size)
        self.__connect()

        # テスト用
        self.size = (10, 20, 10)

    def dump(self, indent=4):
        if not os.path.isdir(Module.dump_directory_path):
            os.makedirs(Module.dump_directory_path)

        file_name = Module.make_file_name(self.id)

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
        self.__set_inners_id_dict()
        self.__set_id_of_pins()

    def __set_inners_id_dict(self):
        self.__inner_id_dict = {inner.id: i for i, inner in enumerate(self.inners)}

    # 同一テンプレートから違うモジュールを生成しない場合
    def __set_id_of_pins(self):
        inner_type_dict = {inner.type_name: inner.id for inner in self.inners}

        for key in ['initializations', 'operations']:
            for i in range(len(self.circuit[key])):
                element = self.circuit[key][i]
                if element['type'] != 'pin': continue
                type_name = element['module']
                self.circuit[key][i]['module'] = inner_type_dict[type_name]

    def __place(self, permissible_error_rate, permissible_size):
        self.__set_spares(permissible_error_rate)
        self.__place_inners(permissible_size)

    def __place_inners(self, permissible_size):
        if self.is_elementary():
            return

        hyperrectangles, inner_ids = self.__make_placement_hyperrectangles()
        base = self.__make_placement_base(permissible_size)

        with tempfile.NamedTemporaryFile('w') as fp:
            json.dump({
                'hyperrectangles': hyperrectangles,
                'base'           : base
            }, fp)

            fp.flush()
            result = self.__exec_subproccess('inners_placement', fp.name)

        hyperrectangles = json.loads(result)['hyperrectangles']
        self.__set_inners_positions(hyperrectangles, inner_ids)

    def __make_placement_hyperrectangles(self):
        hyperrectangles = []
        inner_ids = []

        for inner in self.inners:
            hyperrectangle = {"size": inner.size}
            for i in range(inner.count + inner.spare_count):
                hyperrectangles.append(hyperrectangle)
                inner_ids.append(inner.id)

        return (hyperrectangles, inner_ids)

    def __make_placement_base(self, permissible_size):
        base_size = list(permissible_size) + [0]
        base_position = [0, 0, 0]

        return {'size': base_size, 'position': base_position}

    def __set_inners_positions(self, hyperrectangles, inner_ids):
        for (hyperrectangle, id) in zip(hyperrectangles, inner_ids):
            self.get_inner(id).positions.append(hyperrectangle['position'])

    def __set_spares(self, permissible_error_rate):
        if self.is_elementary():
            return

        spare_counts = self.__optimize_spare_counts(permissible_error_rate)

        for (spare_id, spare_count) in spare_counts.items():
            self.get_inner(spare_id).spare_count = spare_count

        self.__update_error_rate()

    def __update_error_rate(self):
        success_rate = 1.0

        for inner in self.inners:
            inner_success_rate = 0.0

            (e, n, x) = (inner.error_rate, inner.count, inner.spare_count)
            for i in range(x + 1):
                inner_success_rate \
                    += Util.combination(n + x, n + i) * pow(e, x - i) * pow(1.0 - e, n + i)

            success_rate *= inner_success_rate

        self.error_rate = 1.0 - success_rate

    def __optimize_spare_counts(self, permissible_error_rate):
        inners_dict = self.__make_spare_optimization_inners_dict()

        with tempfile.NamedTemporaryFile('w') as fp:
            # 順序保持のため必要
            ordered_inner_ids = self.__write_spare_optimization_input_file(inners_dict, fp)

            cmd = Module.commands['spare_optimization'] % (fp.name, permissible_error_rate)
            process = subprocess.Popen(cmd, shell=True, \
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            stdout = process.communicate()[0]

        spare_counts = list(map(int, stdout.decode('utf-8').rstrip().split(',')))

        return {id: count for (id, count) in zip(ordered_inner_ids, spare_counts)}

    # キーはid
    # 値は[コスト, エラー率, 個数]
    def __make_spare_optimization_inners_dict(self):
        return {inner.id: [
            reduce(lambda x, y: x * y, inner.size),
            inner.error_rate,
            inner.count
        ] for inner in self.inners}

    def __write_spare_optimization_input_file(self, inners_dict, fp):
        writer = csv.writer(fp)
        ordered_inner_ids = []

        for (inner_id, inner) in inners_dict.items():
            writer.writerow(inner)
            ordered_inner_ids.append(inner_id)
        fp.flush()

        return ordered_inner_ids

    def __parallelize(self):
        with tempfile.NamedTemporaryFile('w') as fp:
            json.dump(self.to_qc(), fp)
            fp.flush()

            cmd = Module.commands['parallelization'] % (fp.name)
            process = subprocess.Popen(cmd, shell=True, \
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            stdout = process.communicate()[0]

        icpm = Converter.to_icpm(json.loads(stdout.decode('utf-8')))
        self.circuit['operations'] = icpm.get('circuit', {}).get('operations', [])

        #self.set_bits()

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
