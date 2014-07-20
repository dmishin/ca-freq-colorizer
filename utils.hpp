#ifndef __UTILS_HPP_INCLUDED__
#define __UTILS_HPP_INCLUDED__

//I hate C-style for cycle
#define FOR_RANGE(type, var, start, end) for(type var=(start), __end=(end); var!=__end; ++var)

inline int wrap( int x, int h ){
  if ( x >= h ) return x - h;
  if ( x < 0) return x + h;
  return x;
}

template< FloatT >
inline uint8 clamp_255( FLoatT x )
{
  if (x <=0 ) return 0;
  if (x >=255) return 255;
  return (uint8)x;
}

template< class T >
T sqr( T x)
{
  return x*x;
}


#endif

