class Completion:
    @classmethod
    def icpm(cls, json_obj):
        json_obj['format']  = json_obj.get('format', 'icpm')
        json_obj['circuit'] = json_obj.get('circuit', {})

        circuit = json_obj['circuit']

        circuit['bits']            = circuit.get('bits', [])
        circuit['inputs']          = circuit.get('inputs', [])
        circuit['outputs']         = circuit.get('outputs', [])
        circuit['initializations'] = circuit.get('initializations', [])
        circuit['measurements']    = circuit.get('measurements', [])
        circuit['operations']      = circuit.get('operations', [])

        return json_obj
