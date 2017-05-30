from dashlivesim.dashlib.chunker import *
from sys import argv


if __name__ == '__main__':
    in_file, out_dir, duration, startNr = argv[1], argv[2], int(argv[3],10), int(argv[4],10)
    data = open(in_file, 'rb').read()
    for n, c in enumerate(chunk(data, duration), start=startNr):
        with open('%s/%s.m4s' % (out_dir,n), 'wb') as o:
            o.write(c)
