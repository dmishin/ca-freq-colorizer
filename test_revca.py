from random import randint
from PIL import Image
from revca import evaluate_steps, eval_even, eval_odd, noise_box, BinaryBlockFunc
import numpy
import time

def initial_pattern_2squares(N, R, percentage):
    fld = numpy.zeros((N,N), dtype = numpy.uint8 )
    c = N / 2

    noise_box( fld, c-R, c-R, c, c, percentage )
    noise_box( fld, c, c, c+R, c+R, percentage )

    return fld

def initial_pattern_square(N, R, percentage):
    if isinstance(R, tuple):
        rx, ry = R
    else:
        rx, ry = R,R
    fld = numpy.zeros((N,N), dtype = numpy.uint8 )
    c = N / 2
    noise_box( fld, c-rx, c-ry, c+rx, c+ry, percentage )
    return fld

def plot_population( fld, steps2 ):
    import matplotlib.pyplot as pp
    pop = []
    for i in xrange(steps2):
        pop.append( numpy.sum(fld))
        eval_even(fld)
        eval_odd (fld)
    pop.append( numpy.sum(fld))
    
    pp.plot( pop )
    pp.show()

def show_field( arr ):
    image = Image.fromarray(arr, mode="P")
    image.putpalette( [0,0,0,255,255,255] )
    image.save("field.png")
    


if __name__=="__main__":
    N = 256
    S = 1000
    print "Testing critters algorithm on %dx%d field, %d steps"%(N, N, S)


    singlerot = BinaryBlockFunc( [0,2,8,3,1,5,6,7,4,9,10,11,12,13,14,15] )
    
    if True:
    
        fld = initial_pattern_square(N, (90,10), 1.0)
        t_start = time.time()
        evaluate_steps( fld, S, func=singlerot )
        t_end = time.time()
        dt = t_end - t_start
        print "Finished in %g seconds, %g steps/s"%(dt, S/dt)
        show_field( fld )

    if False:
        plot_population( initial_pattern_square(N, 60, 0.7), S )

