import ctypes
import numpy
import platform
from PIL import Image


def load_module(name):
    import os.path
    plat = platform.system()
    if plat == "Linux":
        ext = ".so"
    elif plat == "Windows":
        ext = ".dll"
    else:
        raise ValueError("Don't know platform "+plat)
    path = os.path.join(os.path.dirname(__file__), name+ext)
    return ctypes.CDLL( path )

_colorizer =  load_module( "_colorizer" )


#must correspond to the typedef i nthe colorizer.hpp
np_float_t = numpy.float64
float_t = ctypes.c_double #same, for ctypes
np_complex_t = numpy.complex128

uint8_array = numpy.ctypeslib.ndpointer(dtype=numpy.uint8,
                                        flags='C_CONTIGUOUS')

float_array = numpy.ctypeslib.ndpointer(dtype=np_float_t,
                                           flags='C_CONTIGUOUS')
_colorizer_put = _colorizer.colorizer_put
_colorizer_put.argtypes = [float_array, uint8_array, ctypes.c_int, float_t]

_colorizer_image = _colorizer.colorizer_image
_colorizer_image.argtypes = [float_array, uint8_array, ctypes.c_int, float_array, float_t]

_colorizer_underflow_protect = _colorizer.colorizer_underflow_protect
_colorizer_underflow_protect.argtypes = [float_array, ctypes.c_int, float_t]

def colorizer_underflow_protect(state, eps=1e-9):
    if not _colorizer_underflow_protect( state, state.size / 4, eps):
        raise ValueError("colorizer_underflow_protect returned false")

def eval_even(arr,  func):
    h, w = arr.shape
    if not _eval_even( func, arr, w, h ):
        raise ValueError("eval_even returned False")

def eval_odd(arr, func):
    h, w = arr.shape
    if not _eval_odd( func, arr, w, h ):
        raise ValueError("eval_odd returned False")

def evaluate_steps(F, steps, start_step, func ):
    for i in xrange(start_step, start_step+steps):
        (eval_even, eval_odd)[i%2](F, func)


def colorizer_put( colorizer_state, cells, decay ):
    if colorizer_state.dtype != np_float_t:
        raise TypeError("state must be int32")
    if colorizer_state.size != cells.size*4:
        raise ValueError("State must have 4 elements for each cell")

    _colorizer_put( colorizer_state, cells, cells.size, decay )

def colorizer_image( colorizer_state, rgb, ks, gamma=1.0 ):
    if colorizer_state.dtype != np_float_t:
        raise TypeError("Sate must be float32")
    if rgb.dtype != numpy.uint8:
        raise TypeError("RGB must be uint8")
    if ks.dtype != np_float_t:
        raise TypeError("ks myst be float32 matrix")
    if ks.shape != (3,3):
        raise ValueError("ks must be 3x3 matrix")
    if colorizer_state.size / 4 != rgb.size / 3:
        raise ValueError("Sizes not match")

    _colorizer_image( colorizer_state, rgb, colorizer_state.size / 4, ks, gamma )

def new_colorizer_state( ncells ):
    return numpy.zeros( (ncells * 4, ), dtype = np_float_t)


class Colorizer(object):
    """Colorization algorithm, using C code"""
    def __init__(self, N, T, gamma=0.3, K=None):
        if not isinstance(N,tuple): N=(N,N)
        self.N = N
        self.time = T
        self.k = 0.01 ** (1.0/T)
        self.gamma = gamma
        self.rgb = numpy.zeros( N+(3,), dtype = numpy.uint8 )
        self.frames = 0
        self.underflow_protect_every = 100
        self.underflow_treshold = 1e-9

        #self.state = numpy.random.random( N+(4,) ).astype(np_float_t)*100 
        self.state = new_colorizer_state( N[0]*N[1] )

        if K is None:
            #since 
            self.K = numpy.array(
                [[1384, 0, 0  ],
                 [0, 8000.0, -1000],
                 [0, 0, 6666]],
                dtype = np_float_t) / T
        else:
            K = numpy.asarray(K, dtype=np_float_t)
            if K.shape != (3,3):
                raise ValueError("K must be 3x3")
            self.K = K / T
        
    def put(self, fld):
        colorizer_put( self.state, fld, self.k )
        self.frames += 1
        if self.frames >= self.underflow_protect_every:
            self.frames = 0
            colorizer_underflow_protect( self.state, self.underflow_treshold )

    def image(self):
        rgb = self.rgb
        colorizer_image( self.state, rgb, self.K, self.gamma )
        return Image.fromarray( rgb )


class ColorizerNP(object):
    """Colorization algorithm in pure Python + Numpy"""
    def __init__(self, N, T, gamma=0.3, K=None):
        if not isinstance(N,tuple): N=(N,N)
        self.N = N
        self.time = T
        self.k = 0.01 ** (1.0/T)
        self.gamma = gamma
        self.rgb = numpy.zeros( N+(3,), dtype = numpy.uint8 )
        self.state0 = numpy.zeros( N, dtype = np_float_t )
        self.state1 = numpy.zeros( N, dtype = np_float_t )
        self.state2 = numpy.zeros( N, dtype = np_complex_t )
        self.frames = 0
        self.delta = 1e-8
        self.underflow_protect_every = 100

        if K is None:
            #since 
            self.K = numpy.array(
                [[1384, 0, 0  ],
                 [0, 8000.0, -1000],
                 [0, 0, 6666]],
                dtype = np_float_t) / T
        else:
            K = numpy.asarray(K, dtype=np_float_t)
            if K.shape != (3,3):
                raise ValueError("K must be 3x3")
            self.K = K / T
        
    def put(self, fld):
        self.state0 *= self.k
        self.state0 += fld

        self.state1 *= -self.k
        self.state1 += fld

        self.state2 *= numpy.complex(0,self.k)
        self.state2 += fld
        self.frames += 1
        if self.frames > self.underflow_protect_every:
            self.underflow_protect()
            self.frames = 0
    def underflow_protect(self):
        def clean_zeros(arr, eps):
            arr *= numpy.abs(arr) > eps
        clean_zeros(self.state0, self.delta)
        clean_zeros(self.state1, self.delta)
        clean_zeros(self.state2, self.delta)

        #self.state0 *= self.sta
        #self.state1 += self.delta
        #self.state2 += numpy.complex(self.delta, self.delta)
        print "#### executed underflow protection"

    def image(self):
        N2 = self.state0.size

        NN = numpy.zeros( (3, N2), dtype = np_float_t )
        numpy.abs( self.state0.ravel(), out = NN[0, :] )
        numpy.abs( self.state1.ravel(), out = NN[1, :] )
        numpy.abs( self.state2.ravel(), out = NN[2, :] )
        #nuw multiply by K and convert to RGB

        a = 255.0 ** ((1-self.gamma)/self.gamma) #see below, why.

        f_rgb = numpy.dot(self.K*a, NN ) #0..255*a

        #gamma correction koefficient, preserving saturation
        gamma_k = numpy.nan_to_num(numpy.max( f_rgb, axis=0 )**(self.gamma - 1))         #inf...(255*a)^(gamma-1)
        f_rgb *= gamma_k # 0... (255*a)^gamma
        #(255*a)^gamma = 255
        # 255^*(gamma-1) = a^(-gamma)
        # a = 255^((1-gamma)/gamma)

        #convert to 8-byte rgb
        numpy.clip( f_rgb[0,:].reshape(self.N), 0, 255, out = self.rgb[:,:,0] )
        numpy.clip( f_rgb[1,:].reshape(self.N), 0, 255, out = self.rgb[:,:,1] )
        numpy.clip( f_rgb[2,:].reshape(self.N), 0, 255, out = self.rgb[:,:,2] )

        return Image.fromarray( self.rgb )


