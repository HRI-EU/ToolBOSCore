/*
 *  HelloWorld library
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


#include "HelloWorld.h"


/*--------------------------------------------------------------------------*/
/* Private definitions and datatypes                                        */
/*--------------------------------------------------------------------------*/


#define HELLOWORLD_VALID    (0x900db00f)
#define HELLOWORLD_INVALID  (0xdeadb00f)


/*--------------------------------------------------------------------------*/
/* Private prototypes                                                       */
/*--------------------------------------------------------------------------*/


void HelloWorld_exampleFunction( HelloWorld *self );


/*--------------------------------------------------------------------------*/
/* Public functions                                                         */
/*--------------------------------------------------------------------------*/


HelloWorld* HelloWorld_new( void )
{
    HelloWorld *self = (HelloWorld*)NULL;

    self = ANY_TALLOC( HelloWorld );
    ANY_REQUIRE( self );

    return self;
}


int HelloWorld_init( HelloWorld *self )
{
    ANY_REQUIRE( self );

    Any_memset( (void*)self, 0, sizeof( HelloWorld ) );

    self->valid = HELLOWORLD_VALID;

    return 0;
}


// This method might be used to prepare (setup) some network connection
// or additional resources before usage. You can safely remove it if
// not needed:
//
// int HelloWorld_setup( HelloWorld *self )
// {
//     ANY_REQUIRE( self );
//     ANY_REQUIRE( self->valid == HELLOWORLD_VALID );
//
//     return 0;
// }


void HelloWorld_clear( HelloWorld *self )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( self->valid == HELLOWORLD_VALID );

    Any_memset( (void*)self, 0, sizeof( HelloWorld ) );

    self->valid = HELLOWORLD_INVALID;
}


void HelloWorld_delete( HelloWorld *self )
{
    ANY_REQUIRE( self );

    ANY_FREE( self );
}


/*--------------------------------------------------------------------------*/
/* Private functions                                                        */
/*--------------------------------------------------------------------------*/


void HelloWorld_exampleFunction( HelloWorld *self )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( self->valid == HELLOWORLD_VALID );

    ANY_LOG( 0, "Hello World!", ANY_LOG_INFO );
}


/* EOF */
