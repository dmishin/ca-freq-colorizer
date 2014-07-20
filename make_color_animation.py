from random import randint
from PIL import Image
from revca import evaluate_steps, eval_even, eval_odd, noise_box, BinaryBlockFunc, float_t, np_float_t, np_complex_t, BinaryFunc, eval_life

from colorizer import Colorizer, ColorizerNP

import numpy
import os
import math
import platform
import threading
import time
import pickle

def initial_pattern_square(N, R, percentage):
    if not isinstance(N, tuple):
        N = (N,N)
    
    if N[0]%2 != 0 or N[1]%2 != 0: raise ValueError("N must be even")

    if not isinstance(R, tuple): R = (R,R)
    fld = numpy.zeros(N, dtype = numpy.uint8 )
    cx = N[0] / 2
    cy = N[1] / 2
    rx, ry = R
    noise_box( fld, cx-rx, cy-ry, cx+rx, cy+ry, percentage )
    return fld

def margolus_ca_frames(rule, initial_field, initial_step=0):
    """Generates infinite sequence of field states for block binary cellular automata with Margolus neighborhood.
    Field state is a rectangular Numpy array of uint8.
    Initial fiels will be modified!"""
    fld = initial_field
    step = initial_step
    while True:
        (eval_even, eval_odd)[step%2]( fld, func=rule )
        yield fld
        step += 1

def totalistic_ca_frames(rule, initial_field):
    """generates sequence of frames for the totalistic (Life-like) 
    cellular automaton"""
    fld1 = numpy.zeros(initial_field.shape, initial_field.dtype)
    while True:
        eval_life( rule, fld, fld1 )
        fld, fld1 = fld1, fld
        yield fld

def make_animation(clrzr, frame_sequence, name_pattern, frames, write_every, image_options={}, quiet=False):
    """Create sequence of animated colorized frames from the given frame source"""

    frame_iter = iter(frame_sequence)
    for index in xrange(frames):
        t0 = time.time()
        for i in xrange(write_every):
            clrzr.put(next(frame_iter))
        t1 = time.time()
        name = name_pattern%index
        img = clrzr.image()
        t2 = time.time()
        img.save(name, **image_options)
        t3 = time.time()
        if not quiet:
            print "Saved", name, "eval time: %3g colorize time: %3g save time: %3g"%(t1-t0, t2-t1, t3-t2)


def animation_480():
    N = (480, 640)
    R = 25
    S = 1900
    T = 300
    gamma = 0.2
    singlerot = BinaryBlockFunc( [0,2,8,3,1,5,6,7,4,9,10,11,12,13,14,15] )
    fld = initial_pattern_square(N, (R,R), 0.4)
    noise_box( fld, 75, 480, 405,  482, 1.0 )

    K = numpy.array(
        [[2384, 0, 0  ],
        [0, 12000.0, -2000],
        [0, 0, 8666]])*2

    clrzr = Colorizer(N, T, gamma, K=K)
    frames = margolus_ca_frames( singlerot, fld )
    make_animation( clrzr, frames, "frame%04d.png", 8000, 24 )

def animation_360():
    N = (360, 640)
    R = 40
    S = 1900
    T = 300
    gamma = 0.2
    singlerot = BinaryBlockFunc( [0,2,8,3,1,5,6,7,4,9,10,11,12,13,14,15] )
    fld = initial_pattern_square(N, (R,R), 0.4)
    #noise_box( fld, 310, 960,410,  962, 1.0 )
    noise_box( fld, 75, 480, 285,  482, 1.0 )
    #colorization matrix
    K = numpy.array([[2384, 0, 0  ],
        [0, 12000.0, -2000],
        [0, 0, 8666]])*2
    clrzr = Colorizer(N, T, gamma, K=K)
    frames = margolus_ca_frames(singlerot, fld)
    make_animation( clrzr, frames, "frame%04d.png", 10000, 24 )


def animation_life():
    N = (720, 1280)
    R = 150
    S = 1900
    T = 300
    gamma = 0.2
    life = BinaryFunc( S=2, B=3 )
    hlife = BinaryFunc( S=(2), B=(3,6) )
    longlife = BinaryFunc( S=(), B=(5), R=(3,4) )

    fld = initial_pattern_square(N, (R,R), 0.35)
    noise_box( fld, 310, 960,410,  962, 1.0 )
    #colorization matrix
    K = numpy.array([[2384, 0, 0  ],
        [0, 12000.0, -2000],
        [0, 0, 8666]])*2

    clrzr = Colorizer(N, T, gamma, K=K)
    frames = totalistic_ca_frames(hlife, fld)
    make_animation( clrzr, frames, "frame%04d.png", 9000, 1 )

if __name__=="__main__":

    animation_360()
