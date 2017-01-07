from collections import OrderedDict

class Circuit:
    def __init__(self, raw_circuit):
        self.set_bits(raw_circuit)
        self.set_inputs(raw_circuit)
        self.set_outputs(raw_circuit)
        self.set_initializations(raw_circuit)
        self.set_measurements(raw_circuit)
        self.set_gates(raw_circuit)

    def to_dict(self):
        return OrderedDict((
            ('bits'           , self.bits),
            ('inputs'         , self.inputs),
            ('outputs'        , self.outputs),
            ('initializations', self.initializations.to_dict()),
            ('measurements'   , self.measurements.to_dict()),
            ('gates'          , self.gates.to_dict())
        ))

    def set_bits(self, raw_circuit):
        self.bits = []
        for raw_bit in raw_circuit.get('bits', []):
            self.bits.append(raw_bit)

    def set_inputs(self, raw_circuit):
        self.inputs = []
        for raw_input in raw_circuit.get('inputs', []):
            self.inputs.append(raw_input)

    def set_outputs(self, raw_circuit):
        self.outputs = []
        for raw_output in raw_circuit.get('outputs', []):
            self.outputs.append(raw_output)

    def set_initializations(self, raw_circuit):
        self.initializations = []
        for raw_initialization in raw_circuit.get('initializations', []):
            self.initializations.append(Initialization(raw_initialization))

    def set_measurements(self, raw_circuit):
        self.measurements = []
        for raw_measurement in raw_circuit.get('measurements', []):
            self.measurements.append(Measurement(raw_measurement))

    def set_gates(self, raw_circuit):
        self.gates = []
        for raw_gate in raw_circuit.get('gates', []):
            self.gates.append(Gate(raw_gate))

class IM:
    def __init__(self, raw_initialization):
        self.bit  = raw_initialization['bit']
        self.type = raw_initialization['type'].lower()

    def to_dict(self):
        return OrderedDict((
            ('bit' , self.bit),
            ('type', self.type)
        ))

class Initialization(IM):
    def __init__(self, raw_initialization):
        super().__init__(raw_initialization)

class Measurement(IM):
    def __init__(self, raw_measurement):
        super().__init__(raw_measurement)

class Gate:
    def __init__(self, raw_gate):
        self.type = raw_gate['type'].lower()
        self.set_controls(raw_gate)
        self.set_targets(raw_gate)

    def to_dict(self):
        return OrderedDict((
            ('type'    , self.type),
            ('controls', self.controls),
            ('targets' , self.targets)
        ))

    def set_controls(self, raw_gate):
        self.controls = []
        for raw_control in raw_circuit.get('controls', []):
            self.controls.append(raw_control)

    def set_targets(self, raw_gate):
        self.targets = []
        for raw_target in raw_circuit.get('targets', []):
            self.targets.append(raw_target)
