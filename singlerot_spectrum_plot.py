import numpy
from matplotlib import pyplot as pp

from optparse import OptionParser

def main():
    parser = OptionParser(usage = "%prog [options] file.npz show spectrum\n")


    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("Input file not specified")

    ifile = args[0]
    data = numpy.load(ifile)
    spectrum = data['spectrum']
    pp.plot(spectrum)
    pp.show()

    
if __name__=="__main__":
    main()
