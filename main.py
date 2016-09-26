#!/usr/bin/python3

import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from box import Box
from module import Module

def main():
    Module.dump_directory_path = './results/test/'

    box = Box('T')
    box.deploy(0.4, (20, 49))

if __name__ == '__main__':
    main()
