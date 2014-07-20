all: _revca.so _colorizer.so

_revca.so: revca.cpp revca.hpp utils.hpp colorizer.hpp
	g++ -O3 -Wall -shared revca.cpp -o _revca.so

_colorizer.so: colorizer.cpp colorizer.hpp utils.hpp
	g++ -O3 -Wall -shared colorizer.cpp  -o _colorizer.so

clean: 
	rm _revca.so _colorizer.so

.PHONY: all clean
