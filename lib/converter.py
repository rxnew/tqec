import json
from collections import OrderedDict

class Converter:
    @classmethod
    def to_icpm(cls, json_obj):
        if json_obj['format'] == 'qc':
            return OrderedDict((
                ('format' , 'icpm'),
                ('circuit', cls.qc_to_icpm(json_obj['circuit']))
            ))

    @classmethod
    def to_qc(cls, json_obj):
        if json_obj['format'] == 'icpm':
            return OrderedDict((
                ('format' , 'qc'),
                ('circuit', cls.icpm_to_qc(json_obj['circuit']))
            ))

    @classmethod
    def qc_to_icpm(cls, qc_circuit):
        return QcToIcpmConverter.convert(qc_circuit)

    @classmethod
    def icpm_to_qc(cls, icpm_circuit):
        return IcpmToQcConverter.convert(icpm_circuit)

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
        return [cls.__convert_initialization(qc_initialization) \
                for qc_initialization in qc_initializations]

    @classmethod
    def __convert_measurements(cls, qc_measurements):
        return [cls.__convert_measurement(qc_measurement) \
                for qc_measurement in qc_measurements]

    @classmethod
    def __convert_gates(cls, qc_gates):
        return [cls.__convert_gate(qc_gate) \
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
