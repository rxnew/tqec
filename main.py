#!/usr/bin/python3

__doc__ = """{f}

Usage:
    {f} [-t | --type <type>] [-e | --error <error>] [-s | --size <size>]
    {f} -h | --help

Options:
    -t --type=<type>   template type name        [default: cv]
    -e --error=<error> permissible error rate    [default: 0.0001]
    -s --size=<size>   permissible size          [default: 30,49]
    -h --help          show this screen and exit

""".format(f=__file__)

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from docopt import docopt

from template import Template
from module import Module

script_dir = os.path.dirname(__file__)
result_dir = script_dir + '/results'

def main(type_name, permissible_error_rate, permissible_size):
    if not os.path.isdir(result_dir): os.makedirs(result_dir)

    Template.data_directory_path = script_dir + '/' + Template.data_directory_path
    Module.dump_directory_path = result_dir + '/' + type_name.lower()

    template = Template(type_name)
    template.deploy(permissible_error_rate, permissible_size)

def parse():
    args = docopt(__doc__)
    type_name = args['--type'][0]
    permissible_error_rate = float(args['--error'][0])
    permissible_size = tuple([int(s) for s in args['--size'][0].split(',')])
    return type_name, permissible_error_rate, permissible_size

if __name__ == '__main__':
    args = parse()
    main(*args)
