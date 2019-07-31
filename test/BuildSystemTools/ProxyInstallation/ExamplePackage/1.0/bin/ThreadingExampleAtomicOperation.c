/*
 *  Example of atomic operation usage
 *
 *  Copyright (C)
 *  Honda Research Institute Europe GmbH
 *  Carl-Legien-Str. 30
 *  63073 Offenbach/Main
 *  Germany
 *
 *  UNPUBLISHED PROPRIETARY MATERIAL.
 *  ALL RIGHTS RESERVED.
 *
 *
 *  Description: This example test some atomic functions
 *
 */


#include <Atomic.h>


int main( int argc, char *argv[] )
{
  int i;
  long l;
  long long ll;

  Atomic_set( &i, 0 );
  Atomic_set( &l, 0 );

#if !defined( _MSC_VER ) && !defined(__arm__)
  Atomic64_set( &ll, 0 );
#endif

#define Atomic64_testAndSetB
  ANY_REQUIRE( Atomic_get( &i ) == 0 );
  ANY_REQUIRE( Atomic_get( &l ) == 0 );

#if !defined( _MSC_VER ) && !defined(__arm__)
  ANY_REQUIRE( Atomic64_get( &ll ) == 0 );
#endif

  ANY_TRACE( 0, "%d", i );
  ANY_TRACE( 0, "%ld", l );
#if !defined( _MSC_VER ) && !defined(__arm__)
 ANY_TRACE( 0, "%lld", ll );
#endif

  Atomic_inc( &i );
  Atomic_inc( &l );

#if !defined( _MSC_VER ) && !defined(__arm__)
  Atomic64_inc( &ll );
#endif

  ANY_TRACE( 0, "%d", i );
  ANY_TRACE( 0, "%ld", l );

#if !defined( _MSC_VER) && !defined(__arm__)
  ANY_TRACE( 0, "%lld", ll );
#endif

  return 0;

}


/* EOF */
