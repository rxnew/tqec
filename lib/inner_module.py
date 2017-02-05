import json

from collections import OrderedDict
from functools import reduce

class InnerModule:
    @classmethod
    def load(cls, id):
        from module import Module

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
                    'inputs' : json_object['geometry']['inputs'],
                    'outputs': json_object['geometry']['outputs']
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
                ('position', position),
                ('visual'  , {'transparent': True})
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
