import array
import random
import sys

class PGMWriter():
    def __init__(self, map):
        self.map = map
        self.rows = len(map)
        self.cols = len(map[0])

    def __call__(self):

        # define the width  (columns) and height (rows) of your image
        width = self.cols
        height = self.rows

        buff=array.array('B')

        for r in range(self.rows):
            for c in range(self.cols):
                if self.map[r][c] == 1:
                    buff.append(0)
                else:
                    buff.append(1)


        # open file for writing 
        filename = 'map_pgm.pgm'

        try:
            fout=open(filename, 'wb')
        except IOError, er:
            sys.exit()


        # define PGM Header
        pgmHeader = 'P5' + '\n' + str(width) + '  ' + str(height) + '  ' + str(1) + '\n'

        # write the header to the file
        fout.write(pgmHeader)

        # write the data to the file 
        buff.tofile(fout)

        # close the file
        fout.close()