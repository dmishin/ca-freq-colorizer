

import numpy as np
from matplotlib import pyplot as pp

k1 = np.array([1,1,1,1], dtype=np.double)
k2 = np.array([1,-1,1,-1], dtype=np.double)
i = np.complex(0.0,1.0)
k3 = np.array([1,i,-1,-i])

def func(xs):
    a,b,c = (np.abs((ki*xs).sum()) / 4 for ki in (k1,k2,k3))    
    return np.array([a,b,c])
    

def vecs():
    for a in range(2):
        for b in range(2):
            for c in range(2):
                for d in range(2):
                    yield (a,b,c,d), func((a,b,c,d))

vectors = list(vecs())


for abcd, (x1,x2,x3) in vectors:
    s = x1+x2+x3
    pp.plot( x1/s, x2/s, "bo" )
    print abcd, x1/s, x2/s
pp.plot([0,1,0,0],[0,0,1,0],"r-")
pp.show()
