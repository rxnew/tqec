from module import Module

import json

from collections import OrderedDict
from functools import reduce

class InnerModule:
    @classmethod
    def load(cls, id):
        file_name = Module.make_file_name(id)

        with open(file_name, 'r') as fp:
            json_object = json.load(fp)

        return InnerModule(
            type('InnerModuleType', (), {
                'id'        : json_object['id'],
                'type_name' : json_object['type'],
                'size'      : json_object['size'],
                'error_rate': json_object['error'],
                'geometry'  : {
                    'inputs'    : json_object['geometry']['inputs'],
                    'outputs'   : json_object['geometry']['outputs']
                }
            })
        )

    def __init__(self, module):
        self.id          = module.id
        self.type_name   = module.type_name
        self.size        = module.size
        self.error_rate  = module.error_rate
        self.inputs      = module.geometry['inputs']
        self.outputs     = module.geometry['outputs']
        self.count       = 1
        self.spare_count = 0
        self.positions   = []

    def to_output_format(self):
        return [
            OrderedDict((
                ('id'      , self.id),
                ('size'    , self.size),
                ('position', position)
            ))
            for position in self.positions
        ]

    def to_optimization_format(self):
        return {
            'cost'  : self.cost(),
            'error' : self.error_rate,
            'number': self.count
        }

    def cost(self):
        return reduce(lambda x, y: x * y, self.size)

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
