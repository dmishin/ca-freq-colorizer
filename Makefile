all: _revca.so _colorize.so

_revca.so: revca.cpp revca.hpp utils.hpp colorize.hpp
	g++ -march=native -ffast-math -O3 -Wall -shared revca.cpp -o _revca.so

_colorize.so: colorize.cpp colorize.hpp utils.hpp
	g++ -march=native -ffast-math -O3 -Wall -shared colorize.cpp  -o _colorize.so

clean: 
	rm _revca.so _colorize.so

.PHONY: all clean
