import ctypes
import numpy
import platform
from random import randint, random as rand
from colorizer import load_module, uint8_array, float_array, np_float_t, float_t, np_complex_t

_revca =  load_module( "_revca" )

uint8_array = numpy.ctypeslib.ndpointer(dtype=numpy.uint8,
                                        flags='C_CONTIGUOUS')
TYPE_INVERSE = 0
TYPE_PRESERVE = 1
TYPE_RANDOM = 2

_type2name={
    TYPE_INVERSE : "INV",
    TYPE_PRESERVE: "CONST",
    TYPE_RANDOM: "RAND"
}

class BinaryFunc(ctypes.Structure):
    _fields_=[("actions", ctypes.c_uint8 * 9)]
    def __init__(self, S, B, R=[]):
        super(BinaryFunc, self).__init__()
        def value2list(x): 
            if isinstance(x,int): return set((x,))
            else: return set(x)
        S,B,R = map(value2list, (S,B,R))
        if (S & B) or (S & R) or (B & R): raise ValueError("Sets intersecting")
        def put_actions(sums, action):
            for s in sums:
                self.actions[s] = action
        put_actions( range(9), 0 )
        put_actions( S, 1 )
        put_actions( B, 2 )
        put_actions( R, 3 )

    def __str__(self):
        def sums_for_action(a):
            return [s for s in xrange(9) if self.actions[s] == a]
        return "BinaryFunc(%s,%s,%s)"%(sums_for_action(1), sums_for_action(2), sums_for_action(3))
        


class BinaryBlockFunc(ctypes.Structure):
    _fields_=[("y", ctypes.c_uint8 * 16)]
    def __init__(self, values=None):
        super(BinaryBlockFunc, self).__init__()
        if values:
            self.set(values)

    def valid(self):
        return sorted(self.y) == list(range(16))

    def set(self, values):
        values = list(values)
        if len(values) != 16: raise ValueError("Rule must have16 values")
        if not all( v>=0 and v<16 for v in values): raise ValueError("Values must be in range 0..15")
        self.y[:] = values

    def sum_invariance_type(self):
        ftype = None
        is_preserve = True
        is_flipping = True
        for x, y in enumerate(self.y):
            sx = sum(bits4(x))
            sy = sum(bits4(y))
            if sy != sx:
                is_preserve = False
            if sy != 4-sx:
                is_flipping = False
            if not is_preserve and not is_flipping:
                break
        if is_preserve: return TYPE_PRESERVE
        if is_flipping: return TYPE_INVERSE
        return TYPE_RANDOM

    def __str__(self):
        return _type2name[self.sum_invariance_type()] + " " + str(list(self.y))

    def __repr__(self):
        return "BinaryBlockFunc(%s)"%(repr(list(self.y)))

    def parse(self, s, separator=","):
        self.set( int(xii) for xii in (
                xi.strip() for xi in s.split(separator)
                ) if xii )
                  
    def tostring(self):
        return ",".join( str(yi) for yi in self.y )

def make_rinv_func( rfinv_func, 
                    rot2_90,    #bool
                    rot1_angle, #0, 1, -1
                    rot3_angle ):#0, 1, -1
    """From the rotation-flip-invariant function, make a rotation-invariant one"""
    def bin(s):
        return int(s,2)
    ys = list(rfinv_func.y)
    if rot2_90:
        for x in map(bin, ('1100','0101', '1010', '0011')):
            ys[x] = rot90(ys[x], 1)
    if rot1_angle != 0:
        for x in map(bin, ('1000','0100', '0010', '0001')):
            ys[x] = rot90(ys[x], rot1_angle)
    if rot3_angle != 0:
        for x in map(bin, ('0111','1011', '1101', '1110')):
            ys[x] = rot90(ys[x], rot3_angle)

    return BinaryBlockFunc( ys )

def bits4(x):
    return [ (x >> i) & 0x1 for i in xrange(4)]

def from_bits( *abcd):
    b = 0x1
    y = 0x0
    for bit in abcd:
        if bit:
            y = y | b
        b = b << 1
    return y

def inv4(x):
    return x ^ 0xf
    
def rot(x):
    a,b,c,d = bits4(x)
    return from_bits(d,c,b,a)

def rot90(x, direction):
    a,b,c,d = bits4(x)
    # a b  -> c a
    # c d  -> d b
    if direction == 1:
        return from_bits(c, a, d, b)
    elif direction == -1:
        return from_bits(b, d, a, c)
    else: 
        raise ValueError("Bad direction")

def make_rfinv_func( inv_0, #Inverse or not 0000, 1111 blocks
                     inv_2, #inverse or not 1100, 0011, 0101, 1010 blocks
                     inv_2d, #inverse or not diagonal s=2 blocks
                     inv_13, #inverse or not s=1 and s=3 blocks
                     rot_1, #rotate180 or not s=1 blocks
                     rot_3  
                     ):
    """Create a binary transfer function, which is invariant to grid rotations and mirror flips"""
    vals = list(range(16))
    def inv_i(i):
        vals[i] = inv4(vals[i])
    def rot_i(i):
        vals[i] = rot(vals[i])
    def bin(s):
        return int(s,2)
    if inv_0:
        inv_i(bin('0000'))
        inv_i(bin('1111'))
    if inv_2:
        inv_i(bin('1100'))
        inv_i(bin('0011'))
        inv_i(bin('0101'))
        inv_i(bin('1010'))
    if inv_2d:
        inv_i(bin('1001'))
        inv_i(bin('0110'))
    if inv_13:
        inv_i(bin('1000'))
        inv_i(bin('0100'))
        inv_i(bin('0010'))
        inv_i(bin('0001'))
        inv_i(bin('0111'))
        inv_i(bin('1011'))
        inv_i(bin('1101'))
        inv_i(bin('1110'))
    if rot_1:
        rot_i(bin('1000'))
        rot_i(bin('0100'))
        rot_i(bin('0010'))
        rot_i(bin('0001'))
    if rot_3:
        rot_i(bin('0111'))
        rot_i(bin('1011'))
        rot_i(bin('1101'))
        rot_i(bin('1110'))
    assert( list(sorted(vals)) == list(range(16)))
    return BinaryBlockFunc( vals )

BinaryBlockFuncP = ctypes.POINTER(BinaryBlockFunc)
BinaryFuncP = ctypes.POINTER(BinaryFunc)

_eval_even = _revca.evaluate_even
_eval_even.argtypes = [BinaryBlockFuncP, uint8_array, ctypes.c_int, ctypes.c_int ]

_eval_odd = _revca.evaluate_odd
_eval_odd.argtypes = [BinaryBlockFuncP, uint8_array, ctypes.c_int, ctypes.c_int ]


_evaluate_life = _revca.evaluate_life
_evaluate_life.argtypes = [BinaryFuncP, uint8_array, uint8_array, ctypes.c_int, ctypes.c_int ]
def eval_life( func, fld_from, fld_to ):
    if fld_from.shape != fld_to.shape:
        raise ValueError("Shapes don't match")

    h,w = fld_from.shape
    if not _evaluate_life(func, fld_from, fld_to, w, h):
        raise ValueError("evaluate_life reported error")

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


def diagram(func):
    """Make a readable ascii-art diagram for the functon
    
    [..] > [..]
    [.X] > [X.]
    """
    arrow = (">",">")
    separator = (" | ", " | ")

    def x2s(x):
        if x: return "#"
        else: return "."
    def block_dia(x):
        a,b,c,d = bits4(x)
        return ("["+x2s(a)+x2s(b)+"]",
                "["+x2s(c)+x2s(d)+"]" )
    def chain_blocks(xs, separator=" "):
        return [separator.join(row)
                for row in zip(*xs) ]

    def diagram_xs(xs):
        blocks = []
        first = True
        for x in xs:
            if first: first = False
            else: blocks.append(separator)
            blocks.append( block_dia(x))
            blocks.append( arrow )
            blocks.append( block_dia(func.y[x]))
        return chain_blocks( blocks )
    
    def rotations( x ):
        for _ in xrange(4):
            yield x
            x = rot90(x,1)

    lines = []
    lines.extend( diagram_xs( (0x0, 0xf) ) )
    lines.append( "" )
    lines.extend( diagram_xs( rotations( 0x1 ) ) )
    lines.append( "" )
    lines.extend( diagram_xs( rotations( 0x3 ) ) )
    lines.append( "" )
    lines.extend( diagram_xs( (0x9, 0x6) ) )
    lines.append( "" )
    lines.extend( diagram_xs( rotations( 0xe ) ) )

    return "\n".join(lines)
        
def noise_box( fld, x0, y0, x1, y1, percentage=0.5 ):
    num_random_points = int((x1-x0)*(y1-y0)*percentage)
    for y in xrange(y0,y1):
        for x in xrange(x0,x1):
            fld[x,y] = 1 if rand() <= percentage else 0


critters_func = BinaryBlockFunc([15,14,13,3,11,5,6,1,7,9,10,2,12,4,8,0])
