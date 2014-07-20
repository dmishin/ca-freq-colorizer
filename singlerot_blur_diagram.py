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

def show_field( arr ):
    image = Image.fromarray(arr, mode="P")
    image.putpalette( [0,0,0,255,255,255] )
    plat = platform.system()
    if plat == "Windows":
        image.save("field.png")    
    else:
        image.show()

def show_image( img ):
    fname = "image.png"
    plat = platform.system()
    if plat == "Windows":
        img.save(fname)
        print "Saved", fname
        os.system("start "+fname)
    else:
        img.show()

def make_animation(clrzr, rule, initial_pattern, name_pattern, tmax, write_every, image_options={}):

    fld = initial_pattern
    for step in xrange(clrzr.time / 2):
        eval_even( fld, func=rule )
        clrzr.put(fld)
        eval_odd( fld, func=rule )
        clrzr.put(fld)
        
    step = 0
    index = 0
    while step < tmax:
        t0 = time.time()
        for i in xrange(write_every):
            (eval_even, eval_odd)[step%2]( fld, func=rule )
            clrzr.put(fld)
            step += 1
        t1 = time.time()
        name = name_pattern%index
        img = clrzr.image()
        t2 = time.time()
        img.save(name, **image_options)
        t3 = time.time()
        print "Saved", name, "eval time: %3g colorize time: %3g save time: %3g"%(t1-t0, t2-t1, t3-t2)
        index += 1

def make_animation_life(clrzr, rule, initial_pattern, name_pattern, tmax, write_every, image_options={}):

    fld = initial_pattern
    fld1 = numpy.zeros(initial_pattern.shape, initial_pattern.dtype)
        
    step = 0
    index = 0
    while step < tmax:
        t0 = time.time()
        for i in xrange(write_every):
            eval_life( rule, fld, fld1 )
            fld, fld1 = fld1, fld
            clrzr.put(fld)
            step += 1
        t1 = time.time()
        name = name_pattern%index
        img = clrzr.image()
        t2 = time.time()
        img.save(name, **image_options)
        t3 = time.time()
        print "Saved", name, "eval time: %3g colorize time: %3g save time: %3g"%(t1-t0, t2-t1, t3-t2)
        index += 1
            


def animation_480():
    N = (480, 640)
    R = 25
    S = 1900
    T = 300
    gamma = 0.2
    singlerot = BinaryBlockFunc( [0,2,8,3,1,5,6,7,4,9,10,11,12,13,14,15] )
    fld = initial_pattern_square(N, (R,R), 0.4)
    #noise_box( fld, 310, 960,410,  962, 1.0 )
    noise_box( fld, 75, 480, 405,  482, 1.0 )
    #colorization matrix
    K = numpy.array([[2384, 0, 0  ],
        [0, 12000.0, -2000],
        [0, 0, 8666]])*2
    clrzr = Colorizer(N, T, gamma, K=K)
    make_animation( clrzr, singlerot, fld, "frame%04d.png", 24*50000, 24 )

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
    make_animation( clrzr, singlerot, fld, "frame%04d.png", 24*50000, 24 )


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
    make_animation_life( clrzr, hlife, fld, "frame%04d.png", 1*9000, 1 )

if __name__=="__main__":

    animation_360()
