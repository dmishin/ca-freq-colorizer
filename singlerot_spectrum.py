from random import randint
from revca import evaluate_steps, eval_even, eval_odd, noise_box, BinaryBlockFunc
import numpy
import os
import math

def initial_pattern_square(N, R, percentage):
    if N%2 != 0: raise ValueError("N must be even")
    if not isinstance(R, tuple): R = (R,R)
    fld = numpy.zeros((N,N), dtype = numpy.uint8 )
    c = N / 2
    rx, ry = R
    noise_box( fld, c-rx, c-ry, c+rx, c+ry, percentage )
    return fld

def absnorm( fld ):
    afld = numpy.abs(fld)
    return afld / afld.max()

if __name__=="__main__":

    

    N = 128
    R = (40,40)
    percentage = 0.2
    time_chunk = 2**13 #8912
    time_chunks = 1 #total time is time_chunks * time_chunk

    if N%2 != 0: raise ValueError("N must be even")

    #Prepare initial data
    initial_field = numpy.zeros( (N,N), dtype = numpy.uint8 )
    c = N / 2
    rx, ry = R
    noise_box( initial_field, c-rx, c-ry, c+rx, c+ry, percentage )
    rule = BinaryBlockFunc( [0,2,8,3,1,5,6,7,4,9,10,11,12,13,14,15] )#single rotation

    

    #evaluate, accumulating spectra
    accum_spectrum = numpy.zeros( (time_chunk/2+1,) )
    total_spectra = 0

    start_position = 0
    total_pixels = N*N

    pixels_at_once = 256
    while start_position<total_pixels:
        end_position = min(start_position+pixels_at_once, total_pixels)
        print "Calculating stripe", start_position, "to", end_position
        stripe_size = end_position - start_position
        #total memory used: (pixels_at_once * time_chunk) bytes
        fld = initial_field.copy()
        for time_chunk_index in xrange(time_chunks):
            print "Evaluate time chunk", time_chunk_index
            #start evaluating field and accumulating time series for its cells
            time_series = numpy.zeros((stripe_size, time_chunk), dtype=numpy.uint8)
            for t in xrange(time_chunk):
                (eval_even, eval_odd)[t%2]( fld, rule )
                time_series[:,t] = fld.ravel()[start_position : end_position]
            #time series built, now calculate spectrum
            spectrums = numpy.sum(numpy.abs(numpy.fft.rfft( time_series )), 0)
            total_spectra += stripe_size
            accum_spectrum += spectrums
        start_position += pixels_at_once


    print "Accumulated totally", total_spectra, "spectra."
    numpy.savez("singlerot-spectrum.npz", spectrum=accum_spectrum, total_spectra=total_spectra, time_chunk=time_chunk, time_chunks=time_chunks,N=N,R=R,percentage=percentage)
