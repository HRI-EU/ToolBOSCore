/*
 *  ${packageName} library
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


#include "${packageName}.h"


#define ${PACKAGENAME}_VALID    ( ${validFlag} )
#define ${PACKAGENAME}_INVALID  ( ${invalidFlag} )


void ${packageName}_exampleFunction( ${packageName} *self );


${packageName}* ${packageName}_new( void )
{
    ${packageName} *self = (${packageName}*)NULL;

    self = ANY_TALLOC( ${packageName} );
    ANY_REQUIRE( self );

    return self;
}


int ${packageName}_init( ${packageName} *self )
{
    ANY_REQUIRE( self );

    Any_memset( (void*)self, 0, sizeof( ${packageName} ) );

    self->valid = ${PACKAGENAME}_VALID;

    return 0;
}


void ${packageName}_clear( ${packageName} *self )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( self->valid == ${PACKAGENAME}_VALID );

    Any_memset( (void*)self, 0, sizeof( ${packageName} ) );

    self->valid = ${PACKAGENAME}_INVALID;
}


void ${packageName}_delete( ${packageName} *self )
{
    ANY_REQUIRE( self );

    ANY_FREE( self );
}


void ${packageName}_exampleFunction( ${packageName} *self )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( self->valid == ${PACKAGENAME}_VALID );

    ANY_LOG( 0, "Hello World!", ANY_LOG_INFO );
}


/* EOF */
