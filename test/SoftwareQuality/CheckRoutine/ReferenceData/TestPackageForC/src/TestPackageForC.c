/*
*  TestPackageForC.c
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


#include "TestPackageForC.h"


#define TESTPACKAGEFORC_VALID    ( 0x4a467f35UL )
#define TESTPACKAGEFORC_INVALID  ( 0xb33598e5UL )


void TestPackageForC_exampleFunction( TestPackageForC *self );


TestPackageForC* TestPackageForC_new( void )
{
    TestPackageForC *self = (TestPackageForC*)NULL;

    self = ANY_TALLOC( TestPackageForC );
    ANY_REQUIRE( self );

    return self;
}


int TestPackageForC_init( TestPackageForC *self )
{
    ANY_REQUIRE( self );

    Any_memset( (void*)self, 0, sizeof( TestPackageForC ) );

    self->valid = TESTPACKAGEFORC_VALID;

    return 0;
}


void TestPackageForC_clear( TestPackageForC *self )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( self->valid == TESTPACKAGEFORC_VALID );

    Any_memset( (void*)self, 0, sizeof( TestPackageForC ) );

    self->valid = TESTPACKAGEFORC_INVALID;
}


void TestPackageForC_delete( TestPackageForC *self )
{
    ANY_REQUIRE( self );

    ANY_FREE( self );
}


void TestPackageForC_exampleFunction( TestPackageForC *self )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( self->valid == TESTPACKAGEFORC_VALID );

    ANY_LOG( 0, "Hello World!", ANY_LOG_INFO );
}


/* EOF */
