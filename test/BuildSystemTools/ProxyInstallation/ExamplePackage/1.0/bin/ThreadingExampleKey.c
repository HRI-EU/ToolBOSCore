/*
 *  Example of key usage
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
 *  Description: This examples uses a MThreadKey in the general process scope
 *
 */


#include <MThreadKey.h>


int main( int argc, char *argv[] )
{
  MThreadKey *key = NULL;

  key = MThreadKey_new();
  ANY_REQUIRE( key );

  ANY_REQUIRE( MThreadKey_init( key, NULL ) == true );

  ANY_LOG( 0, "Setting the user's value", ANY_LOG_INFO );

  if ( MThreadKey_set( key, key ) == false )
  {
    ANY_LOG( 0, "Unable to set the user's value", ANY_LOG_INFO );
    goto out;
  }

  if ( MThreadKey_get( key ) == (void*)key )
  {
    ANY_LOG( 0, "Checking the user's value, passed!!!", ANY_LOG_INFO );
  }
  else
  {
    ANY_LOG( 0, "User's value are DIFFERENT!!!", ANY_LOG_ERROR );
  }

 out:
  MThreadKey_clear( key );
  MThreadKey_delete( key );

  return 0;
}


/* EOF */
