#include "revca.hpp"
#include <cmath>
#include <algorithm>
#include "utils.hpp"

inline uint8 nonzero( uint8 x )
{
  return x ? 1 : 0;
}

inline void update_block( BinaryBlockFunction *func, uint8 &a00, uint8 &a01, uint8 &a10, uint8 &a11 )
{
  int x = a00 + (a01 << 1) + (a10 << 2) + (a11 << 3 );
  uint8 out = func->output[x];
  if (x != out){
    a00 = nonzero(out & 0x1);
    a01 = nonzero(out & 0x2);
    a10 = nonzero(out & 0x4);
    a11 = nonzero(out & 0x8);
  }
}

int evaluate_even( BinaryBlockFunction *func, uint8 *field, int w, int h )
{
  if (w %2 != 0 || h %2 != 0)
    return 0;

  int offset;
  for( int y = 0; y < h; y += 2){
    offset = y * w;
    for( int x = 0; x < w; x += 2, offset += 2){
      update_block( func,
		      field[offset], field[offset+1],
		      field[offset+w], field[offset+w+1] );
    }
  }
  return 1;
}

int evaluate_odd( BinaryBlockFunction *func, uint8 *field, int w, int h )
{
  if (w %2 != 0 || h %2 != 0)
    return 0;

  int offset;
  for( int y = 1; y < h+1; y += 2){
    uint8 *row1 = field + (y           * w);
    uint8 *row2 = field + (wrap(y+1,h) * w);

    for( int x = 1; x < w+1; x += 2, offset += 2){
      int x2 = wrap(x+1, w);
      update_block( func,
		    row1[x], row1[x2],
		    row2[x], row2[x2] );
    }
  }
  return 1;
}


/**Simple life-like cellular automata algorithm
 */
int evaluate_life( BinaryFunction *func, uint8* from, uint8* to, int w, int h)
{
  FOR_RANGE( int, y, 0, h ){
    int y_p = wrap(y-1,h);
    int y_n = wrap(y+1,h);
    FOR_RANGE( int, x, 0, w ){
      int x_p = wrap(x-1,w);
      int x_n = wrap(x+1,w);
      int s = 
	from[x_p + y_p*w] + from[x + y_p*w] + from[x_n + y_p*w] +
	from[x_p + y*w]                     + from[x_n + y*w] +
	from[x_p + y_n*w] + from[x + y_n*w] + from[x_n + y_n*w];
      if ((s > 8) || (s < 0)) return 0; //bad cell value
      uint8 x1;
      switch(func->actions[s]){
      case 0:
	x1 = 0;
	break;
      case 1:
	x1 = from[x + y*w];
	break;
      case 2:
	x1 = 1;
	break;
      case 3:
	x1 = 1 - from[x + y*w];
	break;
      default:
	return 0;
      };
      to[ x+y*w] = x1;
    }
  }
  return 1;
}
