#!/usr/bin/python3

from box import Box
from module import Module

def main():
    Module.dump_directory_name = './modules/test/'

    box = Box('T')
    box.deploy(0.4, (20, 49))

if __name__ == '__main__':
    main()
