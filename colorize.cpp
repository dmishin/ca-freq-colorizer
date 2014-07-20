#include "revca.hpp"
#include <cmath>
#include <algorithm>
#include <iostream>
#include "utils.hpp"
#include "colorize.hpp"
const int colorizer_states = 4;

int colorizer_put(clr_float_t* colorizer_state, uint8 *cells, int size, clr_float_t decay)
{
  //each byte corresponds to 4 colorisze cells:
  uint8* cells_end = cells + size;
  while(cells != cells_end){
    colorizer_state[0] = colorizer_state[0]*decay + *cells;
    colorizer_state[1] = -colorizer_state[1]*decay + *cells;
    clr_float_t temp = colorizer_state[2];
    colorizer_state[2] = -colorizer_state[3]*decay + *cells;
    colorizer_state[3] = temp * decay;

    colorizer_state += colorizer_states;
    cells ++ ;
  }
  return 1;
}

int colorizer_image(clr_float_t* colorizer_state, uint8 *rgb, int size, clr_float_t *ks, clr_float_t gamma)
{
  clr_float_t gm=0, rm=0, bm=0;
  
  clr_float_t* colorizer_state_end = colorizer_state + size * colorizer_states;
  while( colorizer_state != colorizer_state_end){
    //true gamma
    clr_float_t aa = colorizer_state[0];
    clr_float_t bb = fabs(colorizer_state[1]);
    clr_float_t cc = sqrt(sqr(colorizer_state[2]) + sqr(colorizer_state[3]));

    clr_float_t r,g,b;
    r = ks[0]*aa+ks[1]*bb+ks[2]*cc;
    g = ks[3]*aa+ks[4]*bb+ks[5]*cc;
    b = ks[6]*aa+ks[7]*bb+ks[8]*cc;

    gm = std::max(gm, g);
    rm = std::max(rm, r);
    bm = std::max(bm, b);
    
    //saturation-preserving gamma
    clr_float_t intens = std::max(std::max(r,g),b);
    clr_float_t k;
    if (intens <= 0){
      k = 0;
    }else if (intens <=255)
      k = pow( intens*(1.0f/255.0f), gamma-1 );
    else
      k = 255.0f / intens;

    rgb[0] = clamp_255(r*k);
    rgb[1] = clamp_255(g*k);
    rgb[2] = clamp_255(b*k);
    //move to the next pixel
    rgb += 3;
    colorizer_state += colorizer_states;
  }
  //std::cout<<"Maximal values: R="<<rm<<" G="<<gm<<" B="<<bm<<std::endl;
  return 1;
}


int colorizer_underflow_protect( clr_float_t* colorizer_state, int size, clr_float_t eps)
{
  clr_float_t* end = colorizer_state + (size*colorizer_states);
  for( clr_float_t *pix=colorizer_state; pix !=end; ++pix){
    if (fabs(*pix) < eps)
      *pix = 0;
  }
  return 1;
}
