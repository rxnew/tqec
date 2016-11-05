#!/usr/bin/python3

import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from box import Box
from module import Module

def main(argv):
    type_name = argv[1] if len(argv) > 1 else 'T'

    Module.dump_directory_path = './results/' + type_name.lower() + '/'

    box = Box(type_name)
    box.deploy(0.001, (20, 49))

if __name__ == '__main__':
    main(sys.argv)
