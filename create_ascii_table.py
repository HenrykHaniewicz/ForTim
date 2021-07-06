#!/usr/local/bin/python3.9
# Turn 1D numpy arrays into ASCII format

import sys
import os
import numpy as np

filename = sys.argv[1]

root, ext = os.path.splitext( filename )
outfile = root + ".ascii"

tmp = np.load( filename )

with open( outfile, 'w' ) as f:

    f.write( "# Bins Fit-Flux\n" )
    for i, bin in enumerate( tmp ):
        f.write( str(i) + " " + str(bin) + "\n" )
