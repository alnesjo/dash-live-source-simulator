from dashlivesim.dashlib.chunker import *
from sys import argv


if __name__ == '__main__':
    input, output, duration = argv[1], argv[2], argv[3]
    data = open(input, 'rb').read()
    with open(output, 'wb') as o:
        for c in chunk(data, duration):
            o.write(c)
