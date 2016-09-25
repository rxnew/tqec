import json
import os
import re
import subprocess

class Module:
    counter = 0
    p_gate_type_x = re.compile('braiding|toffoli|mct', re.IGNORECASE)
    dump_directory_name = './'

    @classmethod
    def get_identity(cls):
        identity = cls.counter
        cls.counter += 1
        return identity

    def __init__(self, box, inners, permissible_error_rate, permissible_size):
        self.identity   = Module.get_identity()
        self.type_name  = box.type_name
        self.size       = [0, 0]
        self.error_rate = 0.0
        self.elements   = box.elements
        self.raw_inners = []

        self.set_raw_inners(inners)

        self.place(permissible_error_rate, permissible_size)
        self.parallelize()

    def set_raw_inners(self, inners):
        for inner in inners:
            raw_inner = {
                'type' : inner.type_name,
                'size' : inner.size,
                'error': inner.error_rate
            }
            self.raw_inners.append(raw_inner)

    def place_initializations(self):
        for initialization in self.elements.initializations:
            initialization['column'] = 0

    def place_measurements(self):
        pass

    def place(self, permissible_error_rate, permissible_size):
        a = 0

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

    def dump(self, f=None):
        if not f:
            if not os.path.isdir(Module.dump_directory_name):
                os.makedirs(Module.dump_directory_name)

            file_name = Module.dump_directory_name + 'module_' + \
                        str(self.identity).zfill(4) + '_' + self.type_name.lower() + '.json'
            f = open(file_name, 'w')

        dict_obj = {
            'type'    : self.type_name,
            'id'      : self.identity,
            'size'    : self.size,
            'error'   : self.error_rate,
            'elements': self.elements.to_dict()
        }

        json.dump(dict_obj, f, indent=4)
