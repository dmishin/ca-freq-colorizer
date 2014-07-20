#ifndef __REVCA_HPP_INCLUDED__
#define __REVCA_HPP_INCLUDED__

#ifdef WIN32
#define REVCA_EXPORT __declspec(dllexport)
#else
#define REVCA_EXPORT 
#endif

#include "colorizer.hpp"

struct BinaryBlockFunction{
  uint8 output[16];
};

//actions: 
// 0 - die (x -> 0)
// 1 - unchange (x -> x)
// 2 - born (x -> 1)
// 3 - inverse (x -> 1-x)
struct BinaryFunction{
  uint8 actions[9];
};


extern "C" {
  int REVCA_EXPORT evaluate_even( BinaryBlockFunction *func, uint8 *field, int w, int h );
  int REVCA_EXPORT evaluate_odd( BinaryBlockFunction *func, uint8 *field, int w, int h );

  int REVCA_EXPORT evaluate_life( BinaryFunction *func, uint8* from, uint8* to, int w, int h);
}

#endif
