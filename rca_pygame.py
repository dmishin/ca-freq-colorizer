import pygame
from pygame.locals import *
import numpy 
from revca import *

from random import randint, shuffle
import Tkinter
import tkFileDialog, tkSimpleDialog

from numpy.fft import ifft2, fft2

def with_tkroot( func, *args, **options ):
    root = Tkinter.Tk()
    root.withdraw() # show file dialog without Tkinter window
    options["parent"] = root
    return func( *args, **options )

def save_file_dialog( **options ):
    return with_tkroot(tkFileDialog.asksaveasfilename, **options)

class Field:
    def __init__(self, cells, generation = 0):
        if isinstance(cells, tuple):
            cells = numpy.zeros(cells,dtype=numpy.uint8)
        self.cells = cells
        self.generation = generation

    def next(self, func=critters_func):
        gen = self.generation
        if isinstance(func, (tuple,list)): 
            func = func[gen % len(func)]
        (eval_even, eval_odd)[gen % 2](self.cells, func)
        self.generation = gen+1

    def noise_box( self, x0, y0, x1, y1, percentage=50 ):
        fld = self.cells
        num_random_points = int((x1-x0)*(y1-y0)*percentage)
        for _ in xrange( num_random_points ):
            x = randint( x0, x1 )
            y = randint( y0, y1 )
            fld[x,y] = 1

    def variadic_noise( self, x0, y0, x1, y1 ):
        cells = self.cells
        t = numpy.linspace(0, 1, x1-x0)
        for y in xrange(y0, y1):
            r = numpy.random.rand( 1, x1-x0 )
            cells[ y, x0:x1 ] = (r < t)

    def clear(self):
        self.cells *= 0;

    def toggle_cell(self, x, y):
        cells = self.cells
        (h,w) = cells.shape
        cells[x,y] = 0x1 ^ cells[x,y]

    def save_as(self, fname):
        """Save field in a file, using PIL for data conversion"""
        from PIL import Image
        img = Image.fromarray(self.cells.T,mode="P")
        img.putpalette([0,0,0,255,255,255])
        img.save(fname)

def swap22(func):
    def bin(s):
        return int(s,2)
    y = func.y
    def swp(i,j):
        y[i], y[j] = y[j], y[i]
    swp(bin('1100'),bin('0110'))

def func_fron_index( i ):
    return make_rfinv_func( *[ (i >> bit) & 1 for bit in xrange(6)] )

def bounds( m, delta ):
    fc = m.ravel().copy()
    fc.sort()
    l = int( len(fc) * delta )
    a = fc[l]
    b = fc[-l]
    c = (a+b)*0.5
    scale = lambda x: (x-c)/(1-delta) + c
    return scale(a), scale(b)


rotation_variant_params=sum( ([(False, a, b), (True, a, b)]
                             for a,b in [(0, 0),
                                         (0, 1),
                                         (1, 0),
                                         (1, 1),
                                         (1, -1)]),
                             [] )

if __name__=="__main__":
    pygame.init()
    pygame.font.init()
    
    func_index = 0
    max_func_index = 64
    func_variant_index  = 0
    max_func_variant_index = len(rotation_variant_params)

    size = (640, 480)

    frame_steps = 2
    speeds = [0,2,4,6,8,16,32,64,128,256]
    speed_keys= [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
    fourier_mode = False

    screen = pygame.display.set_mode(size)

    S = 50
    fld = Field( size )

    def new_random_fld():
        fld.clear()
        #fld.noise_box( 256-S, 256-S, 256+S, 256+S, 0.9 )
        fld.variadic_noise( 256-S, 256-S, 256+S, 256+S)

    def current_func():
        func = make_rinv_func( func_fron_index( func_index ),
                               *rotation_variant_params[ func_variant_index ] )
        #swap22(func)
        print "Using function #%d_%d: %s %s"%(func_index, func_variant_index,
                                              func, rotation_variant_params[ func_variant_index ])
        print diagram( func )
        return func

    func = current_func()
    func.parse("0;4;1;12;8;10;6;14; 2;9;5;13;3;11;7;15",";")
    new_random_fld()

    
    surf = pygame.surfarray.make_surface( fld.cells )
    fftsurf = pygame.surfarray.make_surface( fld.cells )
    surf.set_palette([(0,0,0),(255,255,255)])
    fftsurf.set_palette( [(i*i/255,i,i) for i in xrange(256)])
    generation = 0

    while True:
        for event in pygame.event.get():
            if event.type in (QUIT,):
                exit(0)
            elif event.type == KEYDOWN:
                key = event.key

                if key == K_r:
                    new_random_fld()
                elif key in (K_n, K_p):
                    func_index = (func_index + (1 if key == K_n else -1)) % max_func_index
                    func = current_func()
                    new_random_fld()
                elif key in (K_UP, K_DOWN):
                    func_variant_index = (func_variant_index + 
                                          (1 if key == K_UP else -1)) % max_func_variant_index
                    func = current_func()
                    new_random_fld()
                elif key == K_f:
                    fourier_mode = not fourier_mode
                elif key == K_q:
                    exit(0)
                elif key in speed_keys:
                    frame_steps = speeds[speed_keys.index(key)]
                elif key == K_e:
                    rule = with_tkroot(tkSimpleDialog.askstring,
                                       "Set rule","Enter rule",
                                       initialvalue=func.tostring() )
                    if rule:
                        func.parse(rule)
                elif key == K_s:
                    try:
                        path = save_file_dialog(filetypes=[("PNG image:", ".png"),("All files", ".*")])
                        if path:
                            fld.save_as(path)
                    except Exception, e:
                        print "Exception: %s"%(e)
            elif event.type == MOUSEBUTTONDOWN:
                x,y = event.pos
                fld.toggle_cell(x,y)
                

        for i in xrange(frame_steps):
            fld.next( (func))

        if fourier_mode:
            ffc = (numpy.abs(fft2( fld.cells )))
            #ffc = ifft2(numpy.log(fft2( fld.cells ))).real
            
            fmin, fmax = bounds( ffc, 0.1 )
            ffc -= fmin
            ffc *= (255.0/(fmax-fmin))
            pygame.surfarray.blit_array(fftsurf,  ffc.astype( numpy.uint8) )
            screen.blit(fftsurf, (0,0))
        else:
            pygame.surfarray.blit_array(surf,  fld.cells )
            screen.blit(surf, (0,0))

        pygame.display.update()
        if frame_steps == 0:
            pygame.time.delay(100)


def classify_figure(func, figure):
    def minmax(xs):
        pass

#Functions:
# Function: [0, 1, 1, 0, 0, 0] - stringy patterns. Interesing
# Function: [0, 1, 0, 0, 0, 1] - blob gas. mid interest
# Function: [0, 0, 0, 0, 1, 1] - diag gas. mid interest
# Function: [1, 0, 0, 1, 0, 1] - critters?
# Function: [1, 0, 0, 1, 1, 0] - again critters?
# Function: [1, 1, 0, 1, 0, 1] - limited noise
# Function: [0, 1, 1, 1, 0, 0] - growing rectangular patterns
# Function: [0, 1, 1, 1, 0, 0] - non-growing noise
# Function: [1, 1, 0, 1, 1, 1] - Gas, omnidirectional
# Function: [0, 1, 0, 0, 0, 0] - slit stringies. Mostly circular blob
# Function: [0, 1, 0, 1, 0, 0] - new throne-like patterns


# Function: [0, 0, 1, 0, 1, 0] - Gas and borders, nice!


# Combinations:
# 2-20 rich gliders and collisions; small stability islands
# 2-22 rich gliders, but no stability islands
