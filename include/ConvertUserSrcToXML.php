#!/usr/bin/env php
<?php
/*
 *  Converts important fields from the 'userSrc.php' file into XML
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


if( $argc == 1 || $argv[1] == '-h' || $argv[1] == '--help' )
{
  $script = basename( $argv[0] );

  printf( "\nExtracts XML-formatted infos from the provided userSrc.php file, e.g. for\n" );
  printf( "importing into Non-PHP scripts such as ToolBOSCore made in Python.\n\n" );
  printf( "Usage: %s /path/to/userSrc.php\n\n", $script );
  exit( -1 );
}

$filename = $argv[1];

require_once( $filename );


printf( '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' . "\n" );

printf( "<userSrc>\n" );

if( isset( $userSrc_setEnv ) == true )
{
  foreach( $userSrc_setEnv as $key => $value )
  {
    printf( "  <env name=\"%s\">%s</env>\n", $key, $value );
  }
}


if( isset( $userSrc_alias ) == true )
{
  foreach( $userSrc_alias as $key => $value )
  {
    printf( "  <alias name=\"%s\">%s</alias>\n", $key, $value );
  }
}


if( isset( $userSrc_bashCode ) == true )
{
  if( is_array( $userSrc_bashCode ) == true )
  {
    foreach( $userSrc_bashCode as $line )
    {
      printf( "  <code shell=\"bash\">%s</code>\n", $line );
    }
  }
}


if( isset( $userSrc_cmdCode ) == true )
{
  if( is_array( $userSrc_cmdCode ) == true )
  {
    foreach( $userSrc_cmdCode as $line )
    {
      printf( "  <code shell=\"cmd\">%s</code>\n", $line );
    }
  }
}


printf( "</userSrc>\n" );


?>
