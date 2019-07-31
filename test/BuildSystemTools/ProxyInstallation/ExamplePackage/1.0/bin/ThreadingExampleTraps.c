/*
 *  Example of Traps usage
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
 *  Description: This test shows how to use the Traps_* subsystem for getting
 *               backtrace
 *
 */


#include <stdio.h>
#include <string.h>

#include <Any.h>
/* We have to include Traps.h */
#include <Traps.h>

#define EXAMPLE_CRASHTYPE_ANYREQUIRE '1'
#define EXAMPLE_CRASHTYPE_SEGFAULT   '2'


void ExampleTraps_first( char crashType );
void ExampleTraps_second( char crashType );
void ExampleTraps_third( char crashType );


int main( int argc, char *argv[] )
{
  char crashSelection = EXAMPLE_CRASHTYPE_ANYREQUIRE;

  ANY_LOG( 0, "NOTE: This program works if and only if it crashes! Have fun...", ANY_LOG_INFO );

  /* We have to catch signals for traceing errors */
  Traps_trapSynchronousSignal();
  /* We can catch the exit signal for traceing errors */
  Traps_callTraceOnExit(0);

  printf( "\nPlease, select how to crash:\n" );
  printf( " 1) crash with ANY_REQUIRE\n" );
  printf( " 2) crash with segmentation fault\n" );
  printf( "\nPlease, type 1 or 2: " );
  crashSelection = getchar();

  ExampleTraps_first( crashSelection );

  ANY_LOG( 0, "ERROR: A problem occurd! The program was unable to crash!", ANY_LOG_FATAL );
  ANY_LOG( 0, "Please, contact you system administrator.", ANY_LOG_FATAL );

  /* We should release the signals before exiting */
  Traps_untrapSynchronousSignal();

  return -1;
}

/* Private functions */

void ExampleTraps_first( char crashType )
{
  ExampleTraps_second( crashType );
}

void ExampleTraps_second( char crashType )
{
  ExampleTraps_third( crashType );
}

void ExampleTraps_third( char crashType )
{
  /* Here we crash, finally! */
  if ( crashType == EXAMPLE_CRASHTYPE_ANYREQUIRE )
  {
    ANY_REQUIRE_MSG( 0, "Thanks for choosing to crash with ANY_REQUIRE" );
  }
  else
  {
    *((char**)NULL) = (char*)"Crash, please :-)";
  }
}


/* EOF */
