import json

class Compiler:
    def __int__(self, input):
        self.input = input

    def compile(self):
        

    def dump(self, fp):
        output = self.complile()
        json.dump(output, fp)

    def parse_bits(self, bits):
        output = []
        for bit in bits:
            output.append(self.parse_bit(bit))
        return output

    def parse_bit(self, bit):
        id = bit.get('id')
        range = bit.get('range')
        initialization = bit.get('initialization')
        measurement = bit.get('measurement')
        x = [range[0] << 1, range[1] << 1]
        y = id << 1

        output = {'id': id, 'type': 'rough'}

        output['blocks'] = get_blocks(x, y, initialization, measurement)
        output['injectors'] = get_injectors(x, y, initialization)
        output['caps'] = get_caps(x, y, initialization, measurement)

        return output

    def get_blocks(self, x, y, initialization, measurement):
        output = [
            [x[0], y, 0], [x[1], y, 0],
            [x[0], y, 2], [x[1], y, 2]
        ]

        if initialization == 'Z' or initialization == '-Z':
            output.extend([[x[0], y, 0], [x[0], y, 2]])

        if measurement == 'Z' or measurement.get('basis', '') == 'Z':
            output.extend([[x[1], y, 0], [x[1], y, 2]])

        return output

    def get_injectors(self, x, y, initialization):
        if initialization == 'Y' or initialization == 'A':
            return [[x[0], y, 0], [x[0], y, 2]]
        return []

    def get_caps(self, x, y, initialization, measurement):
        output = []

        if initialization is None:
            output.extend([[x[0], y, 0], [x[0], y, 2]])

        if measurement is None:
            output.extend([[x[1], y, 0], [x[1], y, 2]])

        return output

    def get_operation(self, operation):
        type = operation.get('type')
        bits = operation.get('bits')
        step = operation.get('step')
        if type == 'braiding':
            controls = bits.get('controls')
            targets = bits.get('targets')
