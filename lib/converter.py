import json
from collections import OrderedDict

class Converter:
    @classmethod
    def to_icpm(cls, json_object):
        if json_object['format'] == 'qc':
            return OrderedDict((
                ('format' , 'icpm'),
                ('circuit', cls.qc_to_icpm(json_object['circuit']))
            ))

    @classmethod
    def to_qc(cls, json_object):
        if json_object['format'] == 'icpm':
            return OrderedDict((
                ('format' , 'qc'),
                ('circuit', cls.icpm_to_qc(json_object['circuit']))
            ))

    @classmethod
    def qc_to_icpm(cls, qc_circuit):
        return QcToIcpmConverter.convert(qc_circuit)

    @classmethod
    def icpm_to_qc(cls, icpm_circuit):
        return IcpmToQcConverter.convert(icpm_circuit)

    @classmethod
    def icpm_to_tqec(cls, icpm_circuit):
        return IcpmToTqecConverter(icpm_circuit)

    @classmethod
    def complement(cls, json_object):
        if json_object['format'] == 'icpm':
            return cls.complement_icpm(json_object)

    @classmethod
    def complement_icpm(cls, json_object):
        json_object['format']  = json_object.get('format', 'icpm')
        json_object['circuit'] = json_object.get('circuit', {})
        circuit = json_object['circuit']
        circuit['bits']            = circuit.get('bits', [])
        circuit['inputs']          = circuit.get('inputs', [])
        circuit['outputs']         = circuit.get('outputs', [])
        circuit['initializations'] = circuit.get('initializations', [])
        circuit['measurements']    = circuit.get('measurements', [])
        circuit['operations']      = circuit.get('operations', [])
        return json_object

class QcToIcpmConverter:
    @classmethod
    def convert(cls, qc_circuit):
        qc_initializations   = qc_circuit.get('initializations', [])
        qc_measurements      = qc_circuit.get('measurements', [])
        qc_gates             = qc_circuit.get('gates', [])
        icpm_initializations = cls.__convert_initializations(qc_initializations)
        icpm_measurements    = cls.__convert_measurements(qc_measurements)
        icpm_operations      = cls.__convert_gates(qc_gates)

        return OrderedDict((
            ('bits'           , qc_circuit.get('bits', [])),
            ('inputs'         , qc_circuit.get('inputs', [])),
            ('outputs'        , qc_circuit.get('outputs', [])),
            ('initializations', icpm_initializations),
            ('measurements'   , icpm_measurements),
            ('operations'     , icpm_operations)
        ))

    @classmethod
    def __convert_initializations(cls, qc_initializations):
        return [cls.__convert_initialization(qc_initialization)
                for qc_initialization in qc_initializations]

    @classmethod
    def __convert_measurements(cls, qc_measurements):
        return [cls.__convert_measurement(qc_measurement)
                for qc_measurement in qc_measurements]

    @classmethod
    def __convert_gates(cls, qc_gates):
        return [cls.__convert_gate(qc_gate)
                for qc_gate in qc_gates]

    @classmethod
    def __convert_initialization(cls, qc_initialization):
        initialization_type = qc_initialization['type'].lower()

        if initialization_type != 'x' and initialization_type != '-x' and \
           initialization_type != 'z' and initialization_type != '-z':
            return OrderedDict((
                ('bit' , qc_initialization['bit']),
                ('type', 'pin'),
                ('module', initialization_type)
            ))

        return OrderedDict((
            ('bit' , qc_initialization['bit']),
            ('type', initialization_type)
        ))

    @classmethod
    def __convert_measurement(cls, qc_measurement):
        return OrderedDict((
            ('bit' , qc_measurement['bit']),
            ('type', qc_measurement['type'])
        ))

    @classmethod
    def __convert_gate(cls, qc_gate):
        if isinstance(qc_gate, list):
            return [cls.__convert_gate(gate) for gate in qc_gate]

        gate_type = qc_gate['type'].lower()
        controls  = qc_gate.get('controls', [])
        targets   = qc_gate.get('targets', [])

        if gate_type == 'x' and len(controls) == 1:
            return OrderedDict((
                ('type'    , 'cnot'),
                ('controls', controls),
                ('targets' , targets)
            ))

        return OrderedDict((
            ('type'    , 'pin'),
            ('module'  , gate_type),
            ('controls', controls),
            ('targets' , targets)
        ))

class IcpmToQcConverter:
    @classmethod
    def convert(cls, icpm_circuit):
        icpm_initializations = icpm_circuit.get('initializations', [])
        icpm_measurements    = icpm_circuit.get('measurements', [])
        icpm_operations      = icpm_circuit.get('operations', [])
        qc_initializations   = cls.__convert_initializations(icpm_initializations)
        qc_measurements      = cls.__convert_measurements(icpm_measurements)
        qc_gates             = cls.__convert_operations(icpm_operations)

        return OrderedDict((
            ('bits'           , icpm_circuit.get('bits', [])),
            ('inputs'         , icpm_circuit.get('inputs', [])),
            ('outputs'        , icpm_circuit.get('outputs', [])),
            ('initializations', qc_initializations),
            ('measurements'   , qc_measurements),
            ('gates'          , qc_gates)
        ))

    @classmethod
    def __convert_initializations(cls, icpm_initializations):
        return [cls.__convert_initialization(icpm_initialization)
                for icpm_initialization in icpm_initializations]

    @classmethod
    def __convert_measurements(cls, icpm_measurements):
        return [cls.__convert_measurement(icpm_measurement)
                for icpm_measurement in icpm_measurements]

    @classmethod
    def __convert_operations(cls, icpm_operations):
        return [cls.__convert_operation(icpm_operation)
                for icpm_operation in icpm_operations]

    @classmethod
    def __convert_initialization(cls, icpm_initialization):
        initialization_type = icpm_initialization['type'].lower()

        if initialization_type == 'pin':
            initialization_type = icpm_initialization['module']

        return OrderedDict((
            ('bit' , icpm_initialization['bit']),
            ('type', initialization_type)
        ))

    @classmethod
    def __convert_measurement(cls, icpm_measurement):
        return OrderedDict((
            ('bit' , icpm_measurement['bit']),
            ('type', icpm_measurement['type'])
        ))

    @classmethod
    def __convert_operation(cls, icpm_operation):
        if isinstance(icpm_operation, list):
            return [__convert_operation(operation) for operation in icpm_operation]

        operation_type = icpm_operation['type'].lower()

        if operation_type == 'cnot':
            operation_type = 'x'
        elif operation_type == 'pin':
            operation_type = icpm_operation['module']

        return OrderedDict((
            ('type', operation_type),
            ('controls', icpm_operation.get('controls', [])),
            ('targets' , icpm_operation.get('targets', []))
        ))

class IcmToTqecConverter:
    @classmethod
    def convert(cls, icm_circuit):
        icm_initializations = icm_circuit.get('initializations', [])
        icm_measurements    = icm_circuit.get('measurements', [])
        icm_cnots           = icm_circuit.get('cnots', [])
        bit_length          = cls.__calculate_bit_length(icm_cnots)

        logical_qubits = cls.__convert_bits(icm_bits, bit_length)
        logical_qubits = cls.__convert_initializations(icm_initialization, logical_qubits)
        logical_qubits = cls.__convert_measurement(icm_measurements, bit_length, logical_qubits)
        logical_qubits = cls.__convert_cnots(icm_cnots, logical_qubits)

        return OrderedDict((
            ('logical_qubits', logical_qubits)
        ))

    @classmethod
    def __calculate_bit_length(cls, icm_cnots):
        return len(icm_cnots) * 4

    @classmethod
    def __convert_bits(cls, icm_bits, bit_length):
        cls.__max_id = 0
        return [cls.__convert_bit(icm_bit, bit_length) for icm_bit in icm_bits]

    @classmethod
    def __convert_initializations(cls, icm_initializations, logical_qubits):
        return [cls.__convert_initialization(icm_initialization, logical_qubits)
                for icm_initialization in icm_initializations]

    @classmethod
    def __convert_measurements(cls, icm_measurements, logical_qubits, bit_length):
        return [cls.__convert_measurement(icm_measurement, logical_qubits, bit_length)
                for icm_measurement in icm_measurements]

    @classmethod
    def __convert_cnots(cls, icm_cnots, logical_qubits):
        return logical_qubits.extend([
            logical_qubit
            for logical_qubit in cls.__convert_cnot_step(icm_cnot_step, logical_qubits, step)
            for step, icm_cnot_step in enumerate(icm_cnots)
        ])

    @classmethod
    def __convert_bit(cls, icm_bit, bit_length):
        cls.__max_id = max(cls.__max_id, icm_bit)
        x = icm_bit << 1
        blocks = [
            [[x, 0, 0], [x, 0, bit_length]],
            [[x, 2, 0], [x, 2, bit_length]]
         ]
        return OrderedDict((
            ('id'       , icm_bit),
            ('type'     , 'rough'),
            ('blocks'   , blocks),
            ('injectors', []),
            ('caps'     , [])
        ))

    @classmethod
    def __convert_initialization(cls, icm_initialization, logical_qubits):
        initialization_type = icm_initialization['type'].lower()
        initialization_bit  = icm_initialization['bit']
        index = cls.__find_index_of_logical_qubits(initialization_bit, logical_qubits)
        if initialization_type == 'z':
            x = initialization_bit << 1
            block = [[x, 0, 0], [x, 2, 0]]
            logical_qubits[index]['blocks'].append(block)
        return logical_qubits[index]

    @classmethod
    def __convert_measurement(cls, icm_measurement, bit_length, logical_qubits):
        mesurement_type = icm_mesurement['type'].lower()
        mesurement_bit  = icm_mesurement['bit']
        index = cls.__find_index_of_logical_qubits(mesurement_bit, logical_qubits)
        if mesurement_type == 'z':
            x = mesurement_bit << 1
            block = [[x, 0, bit_length], [x, 2, bit_length]]
            logical_qubits[index]['blocks'].append(block)
        return logical_qubits[index]

    @classmethod
    def __convert_cnot_step(cls, icm_cnot_step, step, logical_qubits):
        if not isinstance(icm_cnot_step, list):
            return [cls.__convert_cnot(icm_cnot_step, step, logical_qubits)]
        return [cls.__convert_cnot(icm_cnot, step, logical_qubits)
                for icm_cnot in icm_cnot_step]

    @classmethod
    def __convert_cnot(cls, icm_cnot, step, logical_qubits):
        cls.__max_id += 1
        control_bit = icm_cnot['controls'][0]
        cls.__update_braiding_control_bit(control_bit, step, logical_qubits)
        blocks = cls.__make_braiding_blocks(control_bit, icm_cnot['targets'], step)
        return OrderedDict((
            ('id'       , cls.__max_id),
            ('type'     , 'smooth'),
            ('blocks'   , blocks)
        ))

    @classmethod
    def __update_braiding_control_bit(cls, bit, step, logical_qubits):
        x = bit << 1
        z = step << 2 - 2
        block = [[x, 0, z], [x, 2, z]]
        index = cls.__find_index_of_logical_qubits(bit, logical_qubits)
        logical_qubits[index]['blocks'].append(block)

    @classmethod
    def __make_braiding_blocks(cls, contol_bit, target_bits, step):
        from copy import deepcopy

        bits = sorted([control_bit] + icm_cnot['targets'])
        up = (bits[0] == control_bit)
        x = bits[0] << 1 - 1
        y = 3 if up else 1
        z = step << 2 - 3
        position = [x, y, z]
        blocks = [deepcopy(position)]
        direct = -1

        def get_direct(position_a, position_b):
            for i in range(3):
                if position_a[i] != position_b[i]: return i

        def update_blocks():
            current_direct = get_direct(blocks[-1], position)
            if direct == -1 or current_direct != direct:
                blocks.append(deepcopy(position))
                direct = current_direct

        def toggle_up():
            if up:
                position[1] -= 2
                up = False
            else:
                position[1] += 2
                up = True
            update_blocks()

        for bit in range(bits[0], bits[-1]):
            if bit in bits:
                if up: toggle_up()
            else:
                if not up: toggle_up()
            position[0] += 2
            update_blocks()

        if not up and bits[-1] != control_bit: toggle_up()

        position[2] += 2
        update_blocks()

        for bit in reversed(range(bits[0], bits[-1])):
            if bit == control_bit:
                if up: toggle_up()
            else:
                if not up: toggle_up()
            position[0] -= 2
            update_blocks()

        position[2] -= 2
        update_blocks()

        return blocks

    @classmethod
    def __find_index_of_logical_qubits(cls, id, logical_qubits):
        for i in range(len(logical_qubits)):
            if logical_qubits[i]['id'] == id: return i

class IcpmToTqecConverter:
    @classmethod
    def convert(cls, icpm_circuit):
        icpm_initializations = icpm_circuit.get('initializations', [])
        icpm_measurements    = icpm_circuit.get('measurements', [])
        icpm_operations      = icpm_circuit.get('operations', [])
        self.bit_length      = cls.__calculate_bit_length(icpm_operations)
        self.logical_qubits  = cls.__convert_bits(icpm_bits)
        cls.__convert_initializations(icpm_initializations)
        cls.__convert_measurements(icpm_measurements)
        cls.__convert_operations(icpm_operations)
        tqec_inputs
        tqec_outputs

        return OrderedDict((
            ('inputs'        , icpm_circuit.get('inputs', [])),
            ('outputs'       , icpm_circuit.get('outputs', [])),
            ('logical_qubits', self.logical_qubits.values()),
            ('modules'       , icpm_circuit.get('modules', []))
        ))

    @classmethod
    def __calculate_bit_length(cls, icpm_operations):
        bit_length = 0
        self.operation_times = []

        for icpm_operation_step in icpm_operations:
            if not isinstance(icpm_operation_step, list):
                icpm_operation_step = [icpm_operation_step]

            step_length = 0

            for icpm_operation in icpm_operation_step:
                operation_type = icpm_operation['type'].lower()

                if operation_type == 'cnot':
                    step_length = 4 # 2 * 2
                elif operation_type == 'pin':
                    step_length = 6

            self.operation_times.append(bit_length)
            bit_length += step_length

        return bit_length

    @classmethod
    def __convert_bits(cls, icpm_bits):
        return {icpm_bit: cls.__convert_bit(icpm_bit) for icpm_bit in icpm_bits}

    @classmethod
    def __convert_initializations(cls, icpm_initializations):
        return [cls.__convert_initialization(icpm_initialization) \
                for icpm_initialization in icpm_initializations]

    @classmethod
    def __convert_measurements(cls, icpm_measurements):
        return [cls.__convert_measurement(icpm_measurement) \
                for icpm_measurement in icpm_measurements]

    @classmethod
    def __convert_operations(cls, icpm_operations):
        return [cls.__convert_operation(icpm_operation) \
                for icpm_operation in icpm_operations]

    @classmethod
    def __convert_bit(cls, icpm_bit):
        x = icpm_bit << 1
        blocks = [
            [[x, 0, 0], [x, 0, self.bit_length]],
            [[x, 2, 0], [x, 2, self.bit_length]]
         ]
        return OrderedDict((
            ('id'       , icpm_bit),
            ('type'     , 'rough'),
            ('blocks'   , blocks),
            ('injectors', []),
            ('caps'     , []),
        ))

    @classmethod
    def __convert_initialization(cls, icpm_initialization):
        initialization_bit  = icpm_initialization['bit']
        initialization_type = icpm_initialization['type'].lower()

        x = initialization_bit << 1
        block = [[x, 0, 0], [x, 2, 0]]

        if initialization_type == 'z':
            self.logical_qubits[initialization_bit]['blocks'].append(block)

    @classmethod
    def __convert_measurement(cls, icpm_measurement):
        return OrderedDict((
            ('bit' , icpm_measurement['bit']),
            ('type', icpm_measurement['type'])
        ))

    @classmethod
    def __convert_operation(cls, icpm_operation):
        if isinstance(icpm_operation, list):
            return [__convert_operation(operation) for operation in icpm_operation]

        operation_type = icpm_operation['type'].lower()

        if operation_type == 'cnot':
            operation_type = 'x'
        elif operation_type == 'pin':
            operation_type = icpm_operation['module']

        return OrderedDict((
            ('type', operation_type),
            ('controls', icpm_operation.get('controls', [])),
            ('targets' , icpm_operation.get('targets', []))
        ))
