#!/usr/bin/python3

def main():
    d = {}
    d[('abc', 2, 3)] = 'abc23'
    d[('ace', 2, 4)] = 'ace24'
    key = ('ace', 2, 4)
    print(d.get(key))

if __name__ == '__main__':
    main()
