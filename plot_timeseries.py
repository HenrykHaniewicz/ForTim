#!/usr/local/bin/python3
# Plots pulsar time series

import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as clr
from pypulse.archive import Archive
from physics import rms, calculate_rms_matrix
import u


IMUPDATE = None # To compare raw fluxn (frequency only - this will average out the data in time)
EX = None # To compare off-pulse RMS
SAVE = None

if IMUPDATE:
    EX = None

EV_STATE = []

def getSNR( arc ):

    dat = arc.getData()

    return np.max(dat)/rms(dat[arc.opw])




if __name__ == "__main__":

    psr = "J1946+20"

    file = sys.argv[1]

    fe = u.find_frontend( file )

    if EX:
        outfile = f'{psr}_{file[6:11]}_{fe}_{file[21:25]}_{file[26:30]}.zap'
        q = open( outfile, 'w' )
        q.close()
    elif IMUPDATE:
        outfile = f'{psr}_{file[6:11]}_{fe}_{file[21:25]}_{file[28:32]}_imupdate.zap256ascii'
        q = open( outfile, 'w' )
        q.close()
    ar = Archive( file, prepare = True )
    ch = ar.getNsubint()
    chan = ar.getNchan()
    #print(ar.freq[0])

    def on_key(event):
        global EV_STATE
        print( event.key, math.floor(event.xdata), math.floor(event.ydata) )
        if event.key == 'z':
            with open( outfile, 'a+' ) as t:
                t.write( f'{math.floor(event.xdata)} {ar.freq[math.floor(event.xdata)][math.floor(event.ydata)]}\n' )
        elif event.key == 'r':
            with open( outfile, 'a+' ) as t:
                for n in range(ch):
                    t.write( f'{n} {ar.freq[n][math.floor(event.ydata)]}\n' )
        elif event.key == 't': # Use with care!!
            with open( outfile, 'a+' ) as t:
                for f in range(chan):
                    t.write( f'{math.floor(event.xdata)} {ar.freq[math.floor(event.xdata)][f]}\n' )
        elif event.key == 'a':
            EV_STATE.append( (math.floor(event.xdata), math.floor(event.ydata)) )
            if (len(EV_STATE) == 2) and (EV_STATE[0][1] == EV_STATE[1][1]) and (EV_STATE[0][0] != EV_STATE[1][0]):
                with open( outfile, 'a+' ) as t:
                    for n in range( EV_STATE[0][0], EV_STATE[1][0] ):
                        t.write( f'{n} {ar.freq[n][math.floor(event.ydata)]}\n' )
                EV_STATE = []
            elif len(EV_STATE) == 2:
                print( "Resetting window..." )
                EV_STATE = []



    '''

    Plot imshow
    If z is pressed, zap channel
    If a pressed, wait for second 'a' and zap rows

    Zapping done by ar.setWeights() as well as writing to file

    '''
    def on_key_im(event):
        global EV_STATE
        print( event.key, math.floor(event.ydata) )
        if event.key == 'z':
            ar.setWeights( 0.0, t = None, f = math.floor(event.ydata) )
            with open( outfile, 'a+' ) as t:
                for n in range(ch):
                    t.write( f'{n} {ar.freq[n][math.floor(event.ydata)]}\n' )
        elif event.key == 'a':
            EV_STATE.append( math.floor(event.ydata) )
            if (len(EV_STATE) == 2) and (EV_STATE[0] != EV_STATE[1]):
                for m in range( EV_STATE[0], EV_STATE[1] + 1 ):
                    ar.setWeights( 0.0, t = None, f = m )
                with open( outfile, 'a+' ) as t:
                    for m in range( EV_STATE[0], EV_STATE[1] + 1 ):
                        for n in range( ch ):
                            t.write( f'{n} {ar.freq[n][m]}\n' )
                EV_STATE = []
            elif len(EV_STATE) == 2:
                print( "Resetting window..." )
                EV_STATE = []



    if IMUPDATE:

        ar.tscrunch()
        nbin = ar.getNbin()
        data = ar.getData()

        d_fac = IMUPDATE
        if not isinstance(d_fac, int):
            d_fac = 1
        for i in range(d_fac):
            st, ed = i*(chan//d_fac), (i+1)*(chan//d_fac)
            fig = plt.figure( figsize = (7, 7) )
            ax = fig.add_subplot(111)
            cmap = plt.cm.Greens
            ax.imshow( data[st:ed, :], cmap = cmap, interpolation = 'nearest', extent = [ 0, nbin, ed, st ], aspect = 'auto', norm = clr.Normalize( vmin = np.amin(data), vmax = np.amax(data) ) )
            fig.colorbar( plt.cm.ScalarMappable( norm = clr.Normalize( vmin = np.amin(data), vmax = np.amax(data) ), cmap = cmap ), ax = ax )
            cid = fig.canvas.mpl_connect('key_press_event', on_key_im)

            plt.show()

            fig.canvas.mpl_disconnect(cid)

        ar.fscrunch()
        print(getSNR(ar))
        ar.plot( lw = 0.5 )

        if SAVE:
            np.save( f'{psr}_imupdate_scrunched.npy', ar.getData() )


    elif EX:
        data = ar.getData()
        mask = np.zeros( ar.getNbin() )
        np.set_printoptions( threshold = sys.maxsize )
        mask[ar.opw] = 1
        rms = np.array(calculate_rms_matrix( data, mask = mask ))
        rms_mean, rms_std = np.mean(rms), np.std( rms )
        data_lin = np.array([])
        sub_pol = ar.getNsubint() * ar.getNpol()
        num_profs = sub_pol * ar.getNchan()

        d_fac = EX
        for i in range(d_fac):
            st, ed = i*(chan//d_fac), (i+1)*(chan//d_fac)
            fig = plt.figure( figsize = (7, 7) )
            ax = fig.add_subplot(111)
            cmap = plt.cm.Greens
            ax.imshow( rms.T[st:ed, :], cmap = cmap, interpolation = 'nearest', extent = [ 0, ch, ed, st ], aspect = 'auto', norm = clr.Normalize( vmin = 0, vmax = np.amax(rms) ) )
            fig.colorbar( plt.cm.ScalarMappable( norm = clr.Normalize( vmin = 0, vmax = np.amax(rms) ), cmap = cmap ), ax = ax )
            cid = fig.canvas.mpl_connect('key_press_event', on_key)

            plt.show()

            fig.canvas.mpl_disconnect(cid)

        ar.tscrunch()
        ar.fscrunch()
        try:
            print(getSNR(ar))
        except Exception:
            print(ar.shape())
        ar.plot( lw = 0.5 )
        if SAVE:
            np.save( f'{psr}_ex_scrunched.npy', ar.getData() )

    else:
        print( f'Pulsar:\t\t\tPSR {psr}' )
        print( f'Observing band:\t\t{ar.getFrontend()}' )
        print( f'Original data shape:\t{ar.shape()}' )
        ar.tscrunch()
        ar.fscrunch()
        print( f'Crude S/N:\t\t{getSNR(ar):.3f}' )
        ar.plot( lw = 0.5 )
        if SAVE:
            np.save( f'{psr}_raw_scrunched.npy', ar.getData() )
