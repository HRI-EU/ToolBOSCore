/*
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
 *  Description: This test uses the Cond_wait() as sleeping function
 */


#include <stdio.h>
#include <string.h>
#ifndef __MSVC__
#include <unistd.h>
#endif

#include <Any.h>
#include <Cond.h>



int main( int argc, char *argv[] )
{
  Cond *cond;

  cond = Cond_new();
  Cond_init( cond, COND_PRIVATE );

  ANY_LOG( 0, "Wait 5 seconds...", ANY_LOG_INFO );
  Cond_wait( cond, 5000000 );
  ANY_LOG( 0, "Done", ANY_LOG_INFO );

  Cond_clear( cond );
  Cond_delete( cond );

  return 0;
}


/* EOF */
