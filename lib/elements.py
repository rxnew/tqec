from collections import OrderedDict

class Elements:
    def __init__(self, elements):
        self.bits            = elements.get('bits', [])
        self.inputs          = elements.get('inputs', [])
        self.outputs         = elements.get('outputs', [])
        self.initializations = elements.get('initializations', [])
        self.measurements    = elements.get('measurements', [])
        self.operations      = elements.get('operations', [])

    def to_dict(self):
        return OrderedDict((
            ('bits'           , self.bits),
            ('inputs'         , self.inputs),
            ('outputs'        , self.outputs),
            ('initializations', self.initializations),
            ('measurements'   , self.measurements),
            ('operations'     , self.operations)
        ))
