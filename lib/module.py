import json
import os
import re
import subprocess

class Module:
    counter = 0
    p_gate_type_x = re.compile('braiding|toffoli|mct', re.IGNORECASE)
    dump_directory_path = './'

    @classmethod
    def get_identity(cls, type_name):
        identity = cls.counter
        cls.counter += 1
        return identity

    @classmethod
    def get_file_name(cls, identity, type_name):
        return cls.dump_directory_path + 'module_' + \
            str(identity).zfill(4) + '_' + type_name.lower() + '.json'

    @classmethod
    def load_raw(cls, identity, type_name):
        if not identity or not type_name:
            return {}

        file_name = cls.get_file_name(identity, type_name)

        try:
            f = open(file_name, 'r')
        except IOError:
            return {}

        raw = json.load(f)
        return raw

    @classmethod
    def load_raw_inner_format(cls, identity, type_name):
        raw = cls.load_raw(identity, type_name)
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
        self.identity   = Module.get_identity()
        self.type_name  = box.type_name
        self.elements   = box.elements
        self.raw_inners = raw_inners

        self.place(permissible_error_rate, permissible_size)
        self.parallelize()
        self.connect()

    def place(self, permissible_error_rate, permissible_size):
        self.calculate_number_of_spares(permissible_error_rate)
        self.place_initializations()
        self.place_measurements()
        self.place_inners()

        self.error_rate = 0.002
        self.size = [10, 20]

    def place_initializations(self):
        for initialization in self.elements.initializations:
            initialization['column'] = 0

    def place_measurements(self):
        pass

    def place_inners(self):
        pass

    def calculate_number_of_spares(self, permissible_error_rate):
        cmd = './bin/optimize'
        pass

    def parallelize(self):
        qo = self.convert_to_qo()
        file_name = './tmp/' + str(self.identity) + '.qo'
        f = open(file_name, 'w')
        for gate in qo:
            f.write(gate + '\n')
        f.close()

        cmd = './bin/parallelize ' + file_name
        #subprocess.check_call(cmd, shell=True, stdout=devnull)
        #f = open('./tmp/' + str(self.identity) + '_result.qo', 'r')
        #qo = [gate for gate in f]
        #f.close()
        #self.convert_from_qo(qo)

    def connect(self):
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
        elements['modules'] = self.raw_inners

        return {
            'type'    : self.type_name,
            'id'      : self.identity,
            'size'    : self.size,
            'error'   : self.error_rate,
            'elements': elements
        }

    def get_raw_inner_format(self):
        return {
            'type' : self.type_name,
            'id'   : self.identity,
            'size' : self.size,
            'error': self.error_rate
        }

    def dump(self, f=None):
        if not f:
            if not os.path.isdir(Module.dump_directory_path):
                os.makedirs(Module.dump_directory_path)

            file_name = Module.get_file_name(self.identity, self.type_name)
            f = open(file_name, 'w')

        json.dump(self.get_raw(), f, indent=4)
