/*
 *  Main.c
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
 */


/*--------------------------------------------------------------------------*/
/* Includes                                                                 */
/*--------------------------------------------------------------------------*/


#include <Any.h>
#include <stdlib.h>


/*--------------------------------------------------------------------------*/
/* Prototypes                                                               */
/*--------------------------------------------------------------------------*/


void Spam_example( void );


/*--------------------------------------------------------------------------*/
/* Main function                                                            */
/*--------------------------------------------------------------------------*/


int main( int argc, char *argv[] )
{
    Spam_example();

    return EXIT_SUCCESS;
}


/*--------------------------------------------------------------------------*/
/* Private functions                                                        */
/*--------------------------------------------------------------------------*/


void Spam_example( void )
{
    ANY_LOG( 0, "Hello World!", ANY_LOG_INFO );
}


/* EOF */
