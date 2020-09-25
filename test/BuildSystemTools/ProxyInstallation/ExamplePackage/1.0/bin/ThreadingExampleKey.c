/*
 *  Example of key usage
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
