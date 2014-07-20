#ifndef __CRITTERS_HPP_INCLUDED__
#define __CRITTERS_HPP_INCLUDED__

#ifdef WIN32
#define COLORIZER_EXPORT __declspec(dllexport)
#else
#define COLORIZER_EXPORT 
#endif

typedef unsigned char uint8;
typedef double clr_float_t ;

extern "C" {
  int COLORIZER_EXPORT colorizer_put(clr_float_t* colorizer_state, uint8 *cells, int size, clr_float_t decay);
  int COLORIZER_EXPORT colorizer_image(clr_float_t* colorizer_state, uint8 *rgb, int size, clr_float_t *ks, clr_float_t gamma);
  int COLORIZER_EXPORT colorizer_underflow_protect( clr_float_t* colorizer_state, int size, clr_float_t eps);
}

#endif
