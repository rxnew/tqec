from util import Util

import copy
import csv
import functools
import json
import os
import re
import subprocess
import tempfile

class Module:
    dump_directory_path = './'
    counter = 0
    commands = {
        'spare_optimization': './c++/bin/spare_optimization %s %f'
    }
    p_gate_type_x = re.compile('braiding|toffoli|mct', re.IGNORECASE)

    @classmethod
    def get_id(cls, type_name):
        id = cls.counter
        cls.counter += 1
        return id

    @classmethod
    def get_file_name(cls, id, type_name):
        return cls.dump_directory_path + 'module_' + \
            str(id).zfill(4) + '_' + type_name.lower() + '.json'

    @classmethod
    def load_raw(cls, id, type_name):
        if not id or not type_name:
            return None

        file_name = cls.get_file_name(id, type_name)

        with open(file_name, 'r') as fp:
            raw = json.load(fp)

        return raw

    @classmethod
    def load_raw_inner_format(cls, id, type_name):
        raw = cls.load_raw(id, type_name)

        if not raw:
            return None

        raw_inner_format = cls.convert_raw_to_inner_format(raw)

        return raw_inner_format

    @classmethod
    def convert_raw_to_inner_format(cls, raw):
        return {
            'type' : raw.get('type_name', ''),
            'id'   : raw.get('id', ''),
            'size' : raw.get('size', ''),
            'error': raw.get('error', '')
        }

    def __init__(self, box, raw_inners, permissible_error_rate, permissible_size):
        self.id   = Module.get_id(box.type_name)
        self.type_name  = box.type_name
        self.elements   = box.elements
        self.error_rate = box.pure_error_rate
        self.raw_inners = raw_inners

        self.place(permissible_error_rate, permissible_size)
        self.parallelize()
        self.connect()

        # テスト用
        self.size = (10, 20, 10)

    def place(self, permissible_error_rate, permissible_size):
        self.set_spares(permissible_error_rate)

        self.place_initializations()
        self.place_measurements()
        self.place_inners()

    def place_initializations(self):
        for initialization in self.elements.initializations:
            initialization['column'] = 0

    def place_measurements(self):
        pass

    def place_inners(self):
        pass

    def set_spares(self, permissible_error_rate):
        if not self.raw_inners:
            return

        spare_counts = self.optimize_spare_counts(permissible_error_rate)

        for (spare_id, spare_count) in spare_counts.items():
            self.raw_inners[spare_id]['spare'] = spare_count

        self.update_error_rate()

    def update_error_rate(self):
        success_rate = 1.0

        for raw_inner in self.raw_inners.values():
            inner_success_rate = 0.0

            (e, n, x) = (raw_inner['error'], raw_inner['number'], raw_inner['spare'])
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
            functools.reduce(lambda x, y: x * y, raw_inner['size']),
            raw_inner['error'],
            raw_inner['number']
        ] for (inner_id, raw_inner) in self.raw_inners.items()}

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
        elements['modules'] = [raw_inner for raw_inner in self.raw_inners.values()]

        return {
            'type'    : self.type_name,
            'id'      : self.id,
            'size'    : self.size,
            'error'   : self.error_rate,
            'elements': elements
        }

    def get_raw_inner_format(self, count=1):
        return {
            'type'  : self.type_name,
            'id'    : self.id,
            'size'  : self.size,
            'error' : self.error_rate,
            'number': count
        }

    def dump(self, indent=4):
        if not os.path.isdir(Module.dump_directory_path):
            os.makedirs(Module.dump_directory_path)

        file_name = Module.get_file_name(self.id, self.type_name)

        with open(file_name, 'w') as fp:
            json.dump(self.get_raw(), fp, indent=indent)
            fp.flush()
