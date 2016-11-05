from module import Module

import json
from collections import OrderedDict

class InnerModule:
    @classmethod
    def load(cls, id):
        if not id:
            return None

        file_name = Module.get_file_name(id)

        with open(file_name, 'r') as fp:
            raw = json.load(fp)

        return InnerModule(
            type('RawModule', (), {
                'id'        : raw['id'],
                'size'      : raw['size'],
                'error_rate': raw['error'],
                'elements'  : type('RawElements', (), {
                    'bits'   : raw['elements']['bits'],
                    'inputs' : raw['elements']['inputs'],
                    'outputs': raw['elements']['outputs']
                })
            })
        )

    def __init__(self, module):
        self.id          = module.id
        self.size        = module.size
        self.error_rate  = module.error_rate
        self.bits        = module.elements.bits
        self.inputs      = module.elements.inputs
        self.outputs     = module.elements.outputs
        self.count       = 1
        self.spare_count = 0

    def get_input_positions(self):
        return [self.get_raw_io_format(input, 0) for input in self.inputs]

    def get_output_positions(self):
        return [self.get_raw_io_format(output, 1) for output in self.outputs]

    def get_io_positions(self, io, either):
        if type(io) == dict:
            return (io['id'], io['positions'])

        bit = self.bits[io]
        bit_id = bit['id']
        bit_position_x = bit['range'][either]

        return (bit_id, [[bit_position_x, bit_id, 0], [bit_position_x, bit_id, 1]])

    def get_raw(self):
        return OrderedDict((
            ('id'    , self.id),
            ('size'  , self.size),
            ('number', self.count + self.spare_count)
        ))
