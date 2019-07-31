/*
 *  Example of Threads_setPriority()
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
 *  Description: This test demostrate that the MThreads_setPriority() need
 *               to be called only afterwards the MThreads_setSchedPolicy()
 *
 */


#include <stdio.h>
#include <string.h>
#ifndef __MSVC__
#include <unistd.h>
#endif

#include <Any.h>
#include <Threads.h>



int main( int argc, char *argv[] )
{
  Threads *t;

  t = Threads_new();
  Threads_init( t, true );

  ANY_LOG( 0, "You should get a Warning afterwards", ANY_LOG_INFO );

  Threads_setPriority( t, 10 );

  Threads_clear( t );
  Threads_delete( t );

  return 0;
}


/* EOF */
