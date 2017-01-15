#!/usr/bin/python3

import logging
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from template import Template
from module import Module

result_dir = './results'

def main(argv):
    type_name = argv[1] if len(argv) > 1 else 't'

    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)

    Module.dump_directory_path = result_dir + '/' + type_name.lower() + '/'

    template = Template(type_name)
    template.deploy(0.001, (30, 49))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(sys.argv)
