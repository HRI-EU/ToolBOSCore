/*
 *  HelloWorld library
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

    memset( (void*)self, 0, sizeof( HelloWorld ) );

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

    memset( (void*)self, 0, sizeof( HelloWorld ) );

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
