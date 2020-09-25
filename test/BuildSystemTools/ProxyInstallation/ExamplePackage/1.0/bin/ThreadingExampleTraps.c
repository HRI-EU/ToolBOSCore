/*
 *  Example of Traps usage
 *
 *  Copyright (c) Honda Research Institute Europe GmbH
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions are
 *  met:
 *
 *  1. Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *  3. Neither the name of the copyright holder nor the names of its
 *     contributors may be used to endorse or promote products derived from
 *     this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 *  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 *  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 *  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 *  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 *  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 *  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 *  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 *  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 *  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
