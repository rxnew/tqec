from inner_module import InnerModule

class SwitchModule(InnerModule):
    @classmethod
    def make_id(cls, type_name, input_count, output_count):
        return 'sw_' + type_name + '_' + str(input_count) + '_' + str(output_count)

    @classmethod
    def make_size(cls, input_count, output_count):
        return [input_count - 1 << 1, 2, (output_count - (output_count >> 1) + 1) << 1]

    @classmethod
    def make_inputs(cls, input_count):
        inputs = []
        for i in range(input_count):
            x = i << 1
            inputs.append({'positions': [[x, 0, 0], [x, 2, 0]]})
        return inputs

    @classmethod
    def make_outputs(cls, output_count, size):
        outputs = []
        output_count_a = output_count >> 1
        output_count_b = output_count - output_count_a
        for i in range(output_count_b):
            x = i << 1
            outputs.append({'positions': [[x, 0, size[2]], [x, 2, size[2]]]})
        for i in range(output_count_a):
            x = size[0] - (i << 1)
            outputs.append({'positions': [[x, 0, size[2]], [x, 2, size[2]]]})
        return outputs

    def __init__(self, type_name, input_count, output_count):
        size = self.make_size(input_count, output_count)
        super().__init__(type('InnerModuleType', (), {
            'id'        : self.make_id(type_name, input_count, output_count),
            'type_name' : type_name,
            'size'      : size,
            'error_rate': 0.0,
            'geometry'  : {
                'inputs' : self.make_inputs(input_count),
                'outputs': self.make_outputs(output_count, size)
            }
        }))
