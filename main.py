#!/usr/bin/python3

import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from template import Template
from module import Module

def main(argv):
    type_name = argv[1] if len(argv) > 1 else 'T'

    Module.dump_directory_path = './results/' + type_name.lower() + '/'

    template = Template(type_name)
    template.deploy(0.001, (20, 49))

if __name__ == '__main__':
    main(sys.argv)
