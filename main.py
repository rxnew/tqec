#!/usr/bin/python3

__doc__ = """
Usage:
    {f} [[-t | --type <type>] | [-f | --file <file>]] [-e | --error <error>] [-s | --size <size>]
    {f} convert <format> <file>
    {f} -h | --help

Options:
    -t --type=<type>   template type name        [default: cv]
    -f --file=<file>   template file name
    -e --error=<error> permissible error rate    [default: 0.002]
    -s --size=<size>   permissible size          [default: 30,49]
    <format>           output file format
    <file>             input file
    -h --help          show this screen and exit
""".format(f=__file__)

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

import json

from docopt import docopt

from template import Template
from module import Module
from converter import Converter

script_dir = os.path.dirname(__file__)
result_dir = script_dir + '/results'

def main(type_name, file_name, permissible_error_rate, permissible_size):
    if not os.path.isdir(result_dir): os.makedirs(result_dir)

    Template.data_directory_path = script_dir + '/' + Template.data_directory_path
    Module.dump_directory_path = result_dir + '/' + type_name.lower()

    template = Template(type_name, file_name)
    module_id = template.deploy(permissible_error_rate, permissible_size).id
    Module.make_complete_file(module_id)

def convert(format_name, file_name):
    with open(file_name, 'r') as fp:
        json_object = json.load(fp)
    if format_name == 'qc':
        converted_json_object = Converter.to_qc(json_object)
    elif format_name == 'icpm':
        converted_json_object = Converter.to_icpm(json_object)
    elif format_name == 'tqec':
        converted_json_object = Converter.to_tqec(json_object)
    else:
        print('Unknown format \'' + format_name + '\'', file=sys.stderr)
        return
    print(json.dumps(converted_json_object, indent=4))

def parse():
    args = docopt(__doc__)
    if args['convert']: return convert, parse_convert(args)
    return main, parse_main(args)

def parse_main(args):
    if len(args['--file']) != 0:
        file_name = args['--file'][0]
        type_name = 'main_' + os.path.splitext(os.path.basename(file_name))[0]
    else:
        file_name = None
        type_name = args['--type'][0]
    permissible_error_rate = float(args['--error'][0])
    permissible_size = tuple([int(s) for s in args['--size'][0].split(',')])
    return type_name, file_name, permissible_error_rate, permissible_size

def parse_convert(args):
    format_name = args['<format>']
    file_name = args['<file>']
    return format_name, file_name

if __name__ == '__main__':
    func, args = parse()
    func(*args)
