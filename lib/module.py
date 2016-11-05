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
        'spare_optimization': './c++/bin/spare_optimization %s %f'
    }
    p_gate_type_x = re.compile('braiding|toffoli|mct', re.IGNORECASE)

    @classmethod
    def get_id(cls, type_name):
        number = cls.counter.get(type_name, 0)
        cls.counter[type_name] = number + 1

        return type_name.lower() + '_' + str(number)

    @classmethod
    def get_file_name(cls, id):
        return cls.dump_directory_path + 'module_' + id + '.json'

    def __init__(self, box, inners, permissible_error_rate, permissible_size):
        self.id         = Module.get_id(box.type_name)
        self.type_name  = box.type_name
        self.elements   = box.elements
        self.error_rate = box.pure_error_rate
        self.inners     = inners

        self.place(permissible_error_rate, permissible_size)
        self.parallelize()
        self.connect()

        # テスト用
        self.size = (10, 20, 10)

    def place(self, permissible_error_rate, permissible_size):
        self.set_spares(permissible_error_rate)

    def set_spares(self, permissible_error_rate):
        if self.is_elementary():
            return

        spare_counts = self.optimize_spare_counts(permissible_error_rate)

        for (spare_id, spare_count) in spare_counts.items():
            self.inners[spare_id].spare_count = spare_count

        self.update_error_rate()

    def update_error_rate(self):
        success_rate = 1.0

        for inner in self.inners.values():
            inner_success_rate = 0.0

            (e, n, x) = (inner.error_rate, inner.count, inner.spare_count)
            for i in range(x + 1):
                inner_success_rate \
                    += Util.combination(n + x, n + i) * pow(e, x - i) * pow(1.0 - e, n + i)

            success_rate *= inner_success_rate

        self.error_rate = 1.0 - success_rate

    def optimize_spare_counts(self, permissible_error_rate):
        inners_dict = self.create_spare_optimization_inners_dict()

        with tempfile.NamedTemporaryFile('w') as fp:
            # 順序保持のため必要
            ordered_inner_ids = self.write_spare_optimization_input_file(inners_dict, fp)

            cmd = Module.commands['spare_optimization'] % (fp.name, permissible_error_rate)
            process = subprocess.Popen(cmd, shell=True, \
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            stdout = process.communicate()[0]

        spare_counts = list(map(int, stdout.decode('utf-8').rstrip().split(',')))

        return {id: count for (id, count) in zip(ordered_inner_ids, spare_counts)}

    # キーはid
    # 値は[コスト, エラー率, 個数]
    def create_spare_optimization_inners_dict(self):
        return {inner_id: [
            reduce(lambda x, y: x * y, inner.size),
            inner.error_rate,
            inner.count
        ] for (inner_id, inner) in self.inners.items()}

    def write_spare_optimization_input_file(self, inners_dict, fp):
        writer = csv.writer(fp)
        ordered_inner_ids = []

        for (inner_id, inner) in inners_dict.items():
            writer.writerow(inner)
            ordered_inner_ids.append(inner_id)
        fp.flush()

        return ordered_inner_ids

    def parallelize(self):
        qo = self.convert_to_qo()
        file_name = './tmp/' + str(self.id) + '.qo'
        f = open(file_name, 'w')
        for gate in qo:
            f.write(gate + '\n')
        f.close()

        cmd = './bin/parallelize ' + file_name
        #subprocess.check_call(cmd, shell=True, stdout=devnull)
        #f = open('./tmp/' + str(self.id) + '_result.qo', 'r')
        #qo = [gate for gate in f]
        #f.close()
        #self.convert_from_qo(qo)

        self.set_bits()

    def set_bits(self):
        # テスト
        #x = self.get_time_axis_direction_length()
        x = 10

        for (index, bit) in enumerate(self.elements.bits):
            self.elements.bits[index] = {
                'id'   : index,
                'range': [0, x]
                #'source'     : [[0, index, 0], [0, index, 1]],
                #'destination': [[x, index, 0], [x, index, 1]]
            }

    def connect(self):
        cmd = './bin/connection'
        pass

    def convert_to_qo(self):
        qo = []

        for operation in self.elements.operations:
            gate_type = operation.get('type')
            if Module.p_gate_type_x.match(gate_type):
                gate_type = 'X'

            bits = operation.get('bits', {})
            cbits = [self.convert_bit_to_no(bit) for bit in bits.get('controls', [])]
            tbits = [self.convert_bit_to_no(bit) for bit in bits.get('targets', [])]
            cbits_str = ' '.join(map(str, cbits))
            tbits_str = ' '.join(map(lambda no: 'T' + str(no), tbits))

            qo.append(gate_type + ' \\ ' + cbits_str + ' ' + tbits_str + ' \\ \\')

        return qo

    def convert_from_qo(self, qo):
        operations = []

        for gate in qo:
            tmp = list(filter(lambda e: e, re.split(r'\s|\\', gate)))
            gate_type = tmp[0]
            cbits = list(map(int, filter(lambda e: e[0] != 'T', tmp[1:-1])))
            tbits = list(map(lambda e: int(e[1:]), filter(lambda e: e[0] == 'T', tmp[1:-1])))
            step = int(tmp[-1])

            if gate_type == 'X':
                if len(cbits) == 1:
                    gate_type = 'braiding'
                elif len(cbits) == 2:
                    gate_type = 'toffoli'
                else:
                    gate_type = 'mct'

            operation = {'bits': {}}
            operation['type'] = gate_type
            operation['bits']['controls'] = list(map(self.convert_no_to_bit, cbits))
            operation['bits']['targets']  = list(map(self.convert_no_to_bit, tbits))
            operation['column'] = step * 2 - 1

            operations.append(operation)

        self.elements.operations = operations

    def convert_bit_to_no(self, bit):
        if not hasattr(self, 'bit_map'):
            self.bit_map = {bit: i for i, bit in enumerate(self.elements.bits)}

        return self.bit_map.get(bit)

    def convert_no_to_bit(self, no):
        return self.elements.bits[no]

    def get_raw(self):
        elements = self.elements.to_dict()
        elements['modules'] = [inner.get_raw() for inner in self.inners.values()]

        return OrderedDict((
            ('id'      , self.id),
            ('size'    , self.size),
            ('error'   , self.error_rate),
            ('elements', elements)
        ))

    def dump(self, indent=4):
        if not os.path.isdir(Module.dump_directory_path):
            os.makedirs(Module.dump_directory_path)

        file_name = Module.get_file_name(self.id)

        with open(file_name, 'w') as fp:
            json.dump(self.get_raw(), fp, indent=indent)
            fp.flush()

    def is_elementary(self):
        return len(self.inners) == 0
