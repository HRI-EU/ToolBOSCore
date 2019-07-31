/*
 *  Example program: string macros
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


#include <stdlib.h>
#include <stdarg.h>
#include <time.h>
#include <limits.h>
#include <errno.h>
#include <Any.h>

#define EXAMPLE_BUFFLEN            (1024)
#define EXAMPLE_BUFFLEN_SHORT      (24)
#define EXAMPLE_N                  (3)

/* EXAMPLE_STR1 must be bigger than EXAMPLE_STR2 and composed by different
   tokens separate by EXAMPLE_STR2 string  */
#define EXAMPLE_STR1               "foobarfoobar"
#define EXAMPLE_STR1_UPPER         "FOOBARFOOBAR"
#define EXAMPLE_STR2               "bar"
#define EXAMPLE_STR1_LEN           (12)

/* First occurrence of EXAMPLE_STR2 in EXAMPLE_STR1 */
#define EXAMPLE_STR1_FIRSTOCC      "barfoobar"

/* String pointed to by the first occurrence of
   the first EXAMPLE_STR2 character in EXAMPLE_STR1 */
#define EXAMPLE_STR1_FIRSTCHAROCC     "barfoobar"

/* String pointed to by the last occurrence of
   the first EXAMPLE_STR2 character in EXAMPLE_STR1 */
#define EXAMPLE_STR1_LASTCHAROCC     "bar"

/* Maximun length of the initial EXAMPLE_STR1 substring composed only by
   characters in EXAMPLE_STR2 */
#define EXAMPLE_STR1_INITSUBSTRING_INSTR2     (0)

/* Maximun length of the initial EXAMPLE_STR1 substring composed only by
   characters NOT in EXAMPLE_STR2 */
#define EXAMPLE_STR1_INITSUBSTRING_NOTINSTR2  (3)

/* Tokens obteined from the string EXAMPLE_STR1 using the
   string EXAMPLE_STR2 as separator */
#define EXAMPLE_STR1_TOKEN           "foo"
#define EXAMPLE_STR1_N_TOKENS        (2)

#define EXAMPLE_PRINTFUNCNAME( __name, __desc ) \
  ANY_LOG( 0, "Testing function [%s]: %s",\
           ANY_LOG_INFO, #__name, __desc )

/*-------------------------------------------------------------------------*/
/* String functions                                                        */
/*-------------------------------------------------------------------------*/
bool test_strcmp( char *str1, char *str2 )
{
  int result;
  bool retVal;

  /* Test all possible 3 comparison:
     - foobarfoo with bar;
     - bar with foobarfoo;
     - foobarfoo with foo.
   */

  EXAMPLE_PRINTFUNCNAME( Any_strcmp, "Compare the string [" EXAMPLE_STR1
                         "] with the string ["EXAMPLE_STR2"]" );
  result = Any_strcmp( str1, str2 );
  ANY_LOG( 0, "Any_strcmp returns [%d]", ANY_LOG_INFO, result );
  retVal = (result > 0) ? true : false;

  EXAMPLE_PRINTFUNCNAME( Any_strcmp, "Compare the string [" EXAMPLE_STR2
                         "] with the string ["EXAMPLE_STR1"]" );
  result = Any_strcmp( str2, str1 );
  ANY_LOG( 0, "Any_strcmp returns [%d]", ANY_LOG_INFO, result );

  retVal = retVal && (result<0) ? true : false;

  EXAMPLE_PRINTFUNCNAME( Any_strcmp, "Compare the string [" EXAMPLE_STR1
                         "] with the string ["EXAMPLE_STR1"]" );
  result = Any_strcmp( str1, str1 );
  ANY_LOG( 0, "Any_strcmp returns [%d]", ANY_LOG_INFO, result );

  retVal = retVal && (!result) ? true : false;

  return retVal;

}

bool test_strncmp( char *str1, char *str2 )
{
  char buff[EXAMPLE_BUFFLEN];
  int result;
  bool retVal;

  /* Test all possible 3 comparison:
     - foobarfoo with bar;
     - bar with foobarfoo;
     - foobarfoo with foo.
   */

  sprintf( buff, "Compare ONLY the first %d character of the string [%s]"
           " with the string [%s]",
           EXAMPLE_N, str1, str2 );
  EXAMPLE_PRINTFUNCNAME( Any_strncmp, buff );
  result = Any_strncmp( str1, str2, EXAMPLE_N );
  ANY_LOG( 0, "Any_strncmp returns [%d]", ANY_LOG_INFO, result );
  retVal = (result > 0) ? true : false;

  sprintf( buff, "Compare ONLY the first %d character of the string [%s]"
           " with the string [%s]",
           EXAMPLE_N, str2, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_strncmp, buff );
  result = Any_strncmp( str2, str1, EXAMPLE_N );
  ANY_LOG( 0, "Any_strncmp returns [%d]", ANY_LOG_INFO, result );
  retVal = retVal && (result<0) ? true : false;

  sprintf( buff, "Compare ONLY the first %d character of the string [%s]"
           " with the string [%s]",
           EXAMPLE_N, str1, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_strncmp, buff );
  result = Any_strncmp( str1, str1, EXAMPLE_N );
  ANY_LOG( 0, "Any_strncmp returns [%d]", ANY_LOG_INFO, result );
  retVal = retVal && (!result) ? true : false;

  return retVal;

}

bool test_strcasecmp( char *str1, char *str2 )
{
  int result;
  bool retVal;

  /* Test all possible 3 comparison:
     - foobarfoo with bar;
     - bar with foobarfoo;
     - foobarfoo with foo.
   */

  EXAMPLE_PRINTFUNCNAME( Any_strcasecmp, "Compare the string ["EXAMPLE_STR1
                         "] with the string ["EXAMPLE_STR2"] (ignoring case)" );
  result = Any_strcasecmp( str1, str2 );
  ANY_LOG( 0, "Any_strcasecmp returns [%d]", ANY_LOG_INFO, result );
  retVal = (result > 0) ? true : false;

  EXAMPLE_PRINTFUNCNAME( Any_strcasecmp, "Compare the string ["EXAMPLE_STR2
                         "] with the string ["EXAMPLE_STR1"] (ignoring case)" );
  result = Any_strcasecmp( str2, str1 );
  ANY_LOG( 0, "Any_strcasecmp returns [%d]", ANY_LOG_INFO, result );
  retVal = retVal && (result<0) ? true : false;

  EXAMPLE_PRINTFUNCNAME( Any_strcasecmp, "Compare the string ["EXAMPLE_STR1
                         "] with the string ["EXAMPLE_STR1_UPPER"] (ignoring case)" );
  result = Any_strcasecmp( str1, EXAMPLE_STR1_UPPER );
  ANY_LOG( 0, "Any_strcasecmp returns [%d]", ANY_LOG_INFO, result );
  retVal = retVal && ( !result ) ? true : false;

  return retVal;

}

bool test_strncasecmp( char *str1, char *str2 )
{
  char buff[EXAMPLE_BUFFLEN];
  int result;
  bool retVal;

  /* Test all possible 3 comparison:
     - foobarfoo with bar;
     - bar with foobarfoo;
     - foobarfoo with FOO.
   */

  sprintf( buff, "Compare ONLY the first %d character of the string [%s]"
           " with the string [%s] (ignoring case)",
           EXAMPLE_N, str1, str2 );
  EXAMPLE_PRINTFUNCNAME( Any_strncasecmp, buff );
  result = Any_strncasecmp( str1, str2, EXAMPLE_N );
  ANY_LOG( 0, "Any_strncasecmp returns [%d]", ANY_LOG_INFO, result );
  retVal = (result > 0) ? true : false;

  sprintf( buff, "Compare ONLY the first %d character of the string [%s]"
           " with the string [%s] (ignoring case)",
           EXAMPLE_N, str2, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_strncasecmp, buff );
  result = Any_strncasecmp( str2, str1, EXAMPLE_N );
  ANY_LOG( 0, "Any_strncasecmp returns [%d]", ANY_LOG_INFO, result );
  retVal = retVal && (result<0) ? true : false;

  sprintf( buff, "Compare ONLY the first %d character of the string [%s]"
           " with the string [%s] (ignoring case)",
           EXAMPLE_N, str1, EXAMPLE_STR1_UPPER );
  EXAMPLE_PRINTFUNCNAME( Any_strncasecmp, buff );
  result = Any_strncasecmp( str1, EXAMPLE_STR1_UPPER, EXAMPLE_N );
  ANY_LOG( 0, "Any_strncasecmp returns [%d]", ANY_LOG_INFO, result );
  retVal = retVal && (!result) ? true : false;

  return retVal;

}

bool test_strcat( char *str1, char *str2 )
{
  char buff[EXAMPLE_BUFFLEN];
  char *result;
  bool retVal;

  sprintf( buff, "Concatenete the string [%s] to the string [%s]",
           str2, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_strcat, buff );

  result = Any_strcat( str1, str2 );

  ANY_LOG( 0, "Any_strcat returns [%s]", ANY_LOG_INFO, result );
  retVal = (!strcmp( str1, EXAMPLE_STR1 EXAMPLE_STR2 )) ? true : false;

  return retVal;

}

bool test_strncat( char *str1, char *str2 )
{

  char buff[EXAMPLE_BUFFLEN];
  char *result;
  bool retVal;

  sprintf( buff, "Concatenete the first %d characters of the string"
           "[%s] to the string [%s]",
           EXAMPLE_N, str1, str2 );
  EXAMPLE_PRINTFUNCNAME( Any_strncat, buff );

  result = Any_strncat( str2, str1, EXAMPLE_N );

  ANY_LOG( 0, "Any_strcat returns [%s]", ANY_LOG_INFO, result );
  retVal = ( !strncmp( result, EXAMPLE_STR2 EXAMPLE_STR1,
                       strlen( result ) ) ) ? true : false;

  return retVal;

}


bool test_strchr( char *str1, char *str2 )
{
  char *result;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strchr, "Search the first occurrence of the ["
                         EXAMPLE_STR2 "]'s first character in the string ["
                         EXAMPLE_STR1 "]" );

  result = Any_strchr( str1, *str2 );

  if(result)
  {
    ANY_LOG( 0, "Any_strchr returns [%s]", ANY_LOG_INFO, result );
    retVal = ( !strcmp( result, EXAMPLE_STR1_FIRSTCHAROCC )) ? true : false;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strchr returns NULL value", ANY_LOG_WARNING );
  }

  return retVal;

}

bool test_strrchr( char *str1, char *str2 )
{
  char *result;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strrchr, "Search the last occurrence of the ["
                         EXAMPLE_STR2 "]'s first character in the string ["
                         EXAMPLE_STR1 "]" );

  result = Any_strrchr( str1, *str2 );

  if(result)
  {
    ANY_LOG( 0, "Any_strrchr returns [%s]", ANY_LOG_INFO, result );
    retVal = ( !strcmp( result, EXAMPLE_STR1_LASTCHAROCC )) ? true : false;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strchr returns NULL value", ANY_LOG_WARNING );
  }

  return retVal;

}

bool test_strstr( char *str1, char *str2 )
{

  char *result;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strstr,"Search the first occurrence of the string ["
           EXAMPLE_STR2"] in the string [" EXAMPLE_STR1 "]" );

  result = Any_strstr( str1, str2 );

  if(result)
  {
    ANY_LOG( 0, "Any_strstr returns [%s]", ANY_LOG_INFO, result );
    retVal = ( !strcmp( result, EXAMPLE_STR1_FIRSTOCC ) ) ? true : false;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strstr returns NULL value", ANY_LOG_WARNING );
  }

  return retVal;

}

bool test_strlen( char *str1, char *str2 )
{

  int result;
  bool retVal;

  EXAMPLE_PRINTFUNCNAME( Any_strlen, "Get the length of the string ["
                         EXAMPLE_STR1"]" );

  result = Any_strlen( str1 );

  ANY_LOG( 0, "Any_strlen returns [%d]", ANY_LOG_INFO, result );
  retVal = (result == EXAMPLE_STR1_LEN) ? true : false;

  return retVal;

}

bool test_strnlen( char *str1, char *str2 )
{

  int result;
  bool retVal;

  EXAMPLE_PRINTFUNCNAME( Any_strnlen, "Same as above, with strnlen" );

  result = Any_strnlen( str1, EXAMPLE_BUFFLEN_SHORT );

  ANY_LOG( 0, "Any_strnlen returns [%d]", ANY_LOG_INFO, result );
  retVal = (result == EXAMPLE_STR1_LEN) ? true : false;

  return retVal;

}


bool test_strcpy( char *str1, char *str2 )
{
  char buff[EXAMPLE_BUFFLEN];
  char* result;
  bool retVal;

  sprintf( buff, "Copy the string [%s] into the string [%s]",
           str2, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_strcpy, buff );

  result = Any_strcpy( str1, str2 );

  ANY_LOG( 0, "Any_strcpy returns [%s]", ANY_LOG_INFO, result );
  retVal = ( !strcmp( result, str2 ) ) ? true : false;

  return retVal;

}

bool test_strncpy( char *str1, char *str2 )
{

  char buff[EXAMPLE_BUFFLEN];
  char* result;
  bool retVal;

  sprintf( buff, "Copy up to %d characters of the string [%s] into the string [%s]",
           EXAMPLE_N, str2, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_strncpy, buff );

  result = Any_strncpy( str1, str2, EXAMPLE_N );

  ANY_LOG( 0, "Any_strncpy returns [%s]", ANY_LOG_INFO, result );
  retVal = ( !strcmp( result, strcat( str2, &str1[EXAMPLE_N] ) ) ) ? true : false;

  return retVal;

}

bool test_strcoll( char *str1, char *str2 )
{
  int result;
  bool retVal;

  EXAMPLE_PRINTFUNCNAME( Any_strcmp, "Same as Any_strcmp, but using Any_strcoll:"
                         " compare " EXAMPLE_STR1 " with " EXAMPLE_STR2 );

  result = Any_strcoll( str1, str2 );

  if(!errno)
  {
    ANY_LOG( 0, "Any_strcoll returns [%d]", ANY_LOG_INFO, result );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strcoll error!!! Do specified strings contain"
             " invalid characters?", ANY_LOG_INFO );
    return false;
  }
  retVal = (result > 0) ? true : false;

  EXAMPLE_PRINTFUNCNAME( Any_strcmp, "Same as Any_strcmp, but using Any_strcoll:"
                         " compare " EXAMPLE_STR2 " with " EXAMPLE_STR1 );

  result = Any_strcoll( str2, str1 );

  if(!errno)
  {
    ANY_LOG( 0, "Any_strcoll returns [%d]", ANY_LOG_INFO, result );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strcoll error!!! Do specified strings contain"
             " invalid characters?", ANY_LOG_INFO );
    return false;
  }
  retVal = retVal && (result<0) ? true : false;

  EXAMPLE_PRINTFUNCNAME( Any_strcmp, "Same as Any_strcmp, but using Any_strcoll:"
                         " compare " EXAMPLE_STR1 " with " EXAMPLE_STR1 );

  result = Any_strcoll( str1, str1 );

  if(!errno)
  {
    ANY_LOG( 0, "Any_strcoll returns [%d]", ANY_LOG_INFO, result );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strcoll error!!! Do specified strings contain"
             " invalid characters?", ANY_LOG_INFO );
    return false;
  }
  retVal = retVal && (!result) ? true : false;

  return retVal;

}

bool test_strspn( char *str1, char *str2 )
{
  int result;
  bool retVal;

  EXAMPLE_PRINTFUNCNAME( Any_strspn, "Get the maximun length of the initial substring"
                         " of [" EXAMPLE_STR1 "] which contains only characters"
                         " stored into the string ["EXAMPLE_STR2"]" );

  result = Any_strspn( str1, str2 );

  ANY_LOG( 0, "Any_strspn returns [%d]", ANY_LOG_INFO, result );

  retVal = ( result == EXAMPLE_STR1_INITSUBSTRING_INSTR2 ) ? true : false;

  return retVal;

}

bool test_strcspn( char *str1, char *str2 )
{
  int result;
  bool retVal;

  EXAMPLE_PRINTFUNCNAME( Any_strcspn, "Get the maximun length of the initial substring"
                         " of [" EXAMPLE_STR1 "] which DOESN'T contain characters"
                         " stored into the string ["EXAMPLE_STR2"]" );

  result = Any_strcspn( str1, str2 );

  ANY_LOG( 0, "Any_strcspn returns [%d]", ANY_LOG_INFO, result );

  retVal = ( result == EXAMPLE_STR1_INITSUBSTRING_NOTINSTR2 ) ? true : false;

  return retVal;

}

bool test_strtok( char *str1, char *str2 )
{

  char *result;
  int nTokens = 0;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strtok, "Get consecutive tokens from the string ["
                         EXAMPLE_STR1 "] using the string [" EXAMPLE_STR2
                         "] as separator" );

  result= Any_strtok( str1, str2 );

  if( !result )
  {
    ANY_LOG( 0, "Warning: no tokens found", ANY_LOG_WARNING );
  }
  else
  {
    ANY_LOG( 0, "Any_strtok returns token [%s]", ANY_LOG_INFO, result );
    retVal = ( !strcmp( result, EXAMPLE_STR1_TOKEN ) ) ? true : false;
    nTokens++;

    while ( (result = Any_strtok( NULL, str2 )) != NULL )
    {
      ANY_LOG( 0, "Any_strtok returns token [%s]", ANY_LOG_INFO, result );
      retVal = retVal &&
        ( !strcmp( result, EXAMPLE_STR1_TOKEN ) ) ? true : false;
      nTokens++;
    }

    retVal = retVal && ( nTokens == EXAMPLE_STR1_N_TOKENS ) ? true : false;
  }

  return retVal;

}

bool test_strtok_r( char *str1, char *str2 )
{
  char *result;
  char *tmp = NULL;
  int nTokens = 0;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strtok_r,
                         "Same as above, but with Any_strtok_r" );

  result = Any_strtok_r( str1, str2, &tmp );

  if( !result )
  {
    ANY_LOG( 0, "Warning: no tokens found", ANY_LOG_WARNING );
  }
  else
  {
    ANY_LOG( 0, "Any_strtok_r returns token [%s]", ANY_LOG_INFO, result );
    retVal = ( !strcmp( result, EXAMPLE_STR1_TOKEN ) ) ? true : false;
    nTokens++;

    while ( (result = Any_strtok_r( NULL, str2, &tmp )) != NULL )
    {
      ANY_LOG( 0, "Any_strtok_r returns token [%s]", ANY_LOG_INFO, result );
      retVal = retVal &&
        ( !strcmp( result, EXAMPLE_STR1_TOKEN ) ) ? true : false;
      nTokens++;
    }

    retVal = retVal && ( nTokens == EXAMPLE_STR1_N_TOKENS ) ? true : false;
  }

  return retVal;

}

bool test_strsep( char *str1, char *str2 )
{

  char *tmp = str1;
  char *result;
  int nTokens = 0;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strsep, "Get consecutive tokens from the string ["
                         EXAMPLE_STR1 "] using characters from the string ["
                         EXAMPLE_STR2"] as separators" );

  result = Any_strsep( &tmp, str2 );

  if( !result )
  {
    ANY_LOG( 0, "Warning: no tokens found", ANY_LOG_WARNING );
  }
  else
  {
    ANY_LOG( 0, "Any_strsep returns token [%s]", ANY_LOG_INFO, result );
    if( !strcmp( result, EXAMPLE_STR1_TOKEN ) )
    {
      ++nTokens;
    }

    while ( (result = Any_strsep( &tmp, str2 )) != NULL )
    {
      ANY_LOG( 0, "Any_strsep returns token [%s]", ANY_LOG_INFO, result );
      if( !strcmp( result, EXAMPLE_STR1_TOKEN ) )
      {
        ++nTokens;
      }
    }

    retVal = ( nTokens == EXAMPLE_STR1_N_TOKENS ) ? true : false;
  }

  return retVal;

}

bool test_strdup( char *str1, char *str2 )
{
  char *result;
  bool retVal = false;

  EXAMPLE_PRINTFUNCNAME( Any_strdup, "Duplicate the string " EXAMPLE_STR1 );

  result = Any_strdup( str1 );

  if( result )
  {
    ANY_LOG( 0, "Any_strdup returns [%s]", ANY_LOG_INFO, result );
    retVal = ( !strcmp( result, str1 ) ) ? true : false;
    ANY_FREE( result );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_strdup returns NULL value", ANY_LOG_WARNING);
  }

  return retVal;

}

/*-------------------------------------------------------------------------*/
/* String formatting functions                                             */
/*-------------------------------------------------------------------------*/
bool test_printf( char *str1, char *str2 )
{

  char buff[EXAMPLE_BUFFLEN];
  int retVal;
  bool ret = false;

  sprintf( buff, "Print the string [%s] on STDOUT",
           str1 );
  EXAMPLE_PRINTFUNCNAME( Any_printf, buff );

  retVal = Any_printf( "%s", str1 );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_printf returns [%d]", ANY_LOG_INFO, retVal );
    ANY_LOG( 0, "String value: str1[%s]", ANY_LOG_INFO, str1 );
    ret = true;

  }
  else
  {
    ANY_LOG( 0, "Warning: Any_printf returns %d value",
             ANY_LOG_WARNING, retVal );
    ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
  }

  return ret;

}


bool test_fprintf( char *str1, char *str2 )
{

  FILE *f;
  int retVal;
  bool ret = false;

  EXAMPLE_PRINTFUNCNAME( Any_fprintf, "Print the string [" EXAMPLE_STR1
                         "] on file [tmp.txt]" );

  // Open file
  f = fopen( "tmp.txt", "w" );
  if (!f)
  {
    ANY_LOG( 0, "Cannot open file [tmp.txt]", ANY_LOG_ERROR );
  }
  else
  {
    retVal = Any_fprintf( f, "%s", str1 );

    if( retVal > 0 )
    {
      ANY_LOG( 0, "Any_fprintf returns [%d]", ANY_LOG_INFO, retVal );
      ANY_LOG( 0, "String value: str1[%s]", ANY_LOG_INFO, str1 );
      ret = true;
    }
    else
      {
        ANY_LOG( 0, "Warning: Any_fprintf returns %d value",
                 ANY_LOG_WARNING, retVal );
        ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
      }
    fclose( f );
  }

  return ret;
}

bool test_sprintf( char *str1, char *str2 )
{

  int retVal;
  bool ret = false;

  EXAMPLE_PRINTFUNCNAME( Any_sprintf, "Print the string [" EXAMPLE_STR1
                         "] on string [" EXAMPLE_STR2 "]" );

  retVal = Any_sprintf( str1, "%s", str2 );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_sprintf returns [%d]", ANY_LOG_INFO, retVal );
    ANY_LOG( 0, "String values: str1[%s] str2[%s]",
             ANY_LOG_INFO, str1, str2 );
    ret = true;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_sprintf returns %d value",
             ANY_LOG_WARNING, retVal );
    ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
  }

  return ret;

}

bool test_snprintf( char *str1, char *str2 )
{

  char buff[EXAMPLE_BUFFLEN];
  int retVal;
  bool ret = false;

  sprintf( buff, "Print at most %d chars of the string [%s] on string [%s]",
            EXAMPLE_N, str2, str1 );
  EXAMPLE_PRINTFUNCNAME( Any_snprintf, buff );

  retVal = Any_snprintf( str1, EXAMPLE_N, "%s", str2 );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_snprintf returns [%d]", ANY_LOG_INFO, retVal );
    ANY_LOG( 0, "String values: str1[%s] str2[%s]",
             ANY_LOG_INFO, str1, str2 );
    ret = true;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_snprintf returns %d value",
             ANY_LOG_WARNING, retVal );
    ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
  }

  return ret;
}

bool test_scanf( char *str1, char *str2 )
{
  int retVal;
  bool ret = false;

  EXAMPLE_PRINTFUNCNAME( Any_scanf, "Read from STDIN and write to ["
                         EXAMPLE_STR1"] string" );

  retVal = Any_scanf( "%s", str1 );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_scanf returns [%d]", ANY_LOG_INFO, retVal );
    ANY_LOG( 0, "String value: str1[%s]", ANY_LOG_INFO, str1 );
    ret = true;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_scanf returns %d value",
             ANY_LOG_WARNING, retVal );
    ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
  }

  return ret;

}

bool test_fscanf( char *str1, char *str2 )
{

  FILE *f;
  int retVal;
  bool ret = false;

  EXAMPLE_PRINTFUNCNAME( Any_fscanf, "Read from file [tmp.txt] the ["
                         EXAMPLE_STR2 "] string and write it on the["
                         EXAMPLE_STR1 "] string" );

  f = fopen( "tmp.txt", "r+" );

  if(f)
  {

    Any_fprintf( f, "%s", str2 );
    fseek( f, 0, SEEK_SET );

    retVal = Any_fscanf( f, "%11s", str1 );

    if( retVal > 0 )
    {
      ANY_LOG( 0, "Any_fscanf returns [%d]", ANY_LOG_INFO, retVal );
      ANY_LOG( 0, "String value: str1[%s]", ANY_LOG_INFO, str1 );
      ret = true;
    }
    else
    {
      ANY_LOG( 0, "Warning: Any_fscanf returns %d value",
               ANY_LOG_WARNING, retVal );
      ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
    }

    fclose( f );

  }
  else
  {
    ANY_LOG( 0, "Unable to open [tmp.txt] file", ANY_LOG_ERROR );
  }

  return ret;

}

bool test_sscanf( char *str1, char *str2 )
{

  int retVal;
  bool ret = false;

  EXAMPLE_PRINTFUNCNAME( Any_sscanf, "Read from string [" EXAMPLE_STR2
                         "] and write on string [" EXAMPLE_STR1 "]" );

  retVal = Any_sscanf( str2, "%s", str1 );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_sscanf returns [%d]", ANY_LOG_INFO, retVal );
    ANY_LOG( 0, "String values: str1[%s] str2[%s]",
             ANY_LOG_INFO, str1, str2 );
    ret = true;
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_sscanf returns %d value",
             ANY_LOG_WARNING, retVal );
    ANY_LOG( 0, "errno value: [%d]", ANY_LOG_ERROR, errno );
  }

  return ret;

}

/*-------------------------------------------------------------------------*/
/* String formatting functions with variable lenght arguments              */
/*-------------------------------------------------------------------------*/
void test_vsprintf( char *str, const char* fmt, ... )
{
  va_list ap;
  int retVal;

  EXAMPLE_PRINTFUNCNAME( Any_vsprintf, "Same as Any_sprintf" );

  va_start( ap, fmt );
  retVal = Any_vsprintf( str, fmt, ap );
  va_end( ap );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_vsprintf returns [%d]", ANY_LOG_INFO, retVal );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_vsprintf returns %d value",
             ANY_LOG_WARNING, retVal );
  }

}

void test_vsnprintf( char *str, const char* fmt, ... )
{
  va_list ap;
  int retVal;

  EXAMPLE_PRINTFUNCNAME( Any_vsprintf, "Same as Any_snprintf" );

  va_start( ap, fmt );
  retVal = Any_vsnprintf( str, EXAMPLE_N, fmt, ap );
  va_end( ap );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_vsnprintf returns [%d]", ANY_LOG_INFO, retVal );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_vsnprintf returns %d value",
             ANY_LOG_WARNING, retVal );
  }

}

void test_vsscanf( char *str,  const char *fmt, ... )
{
  va_list ap;
  int retVal;

  EXAMPLE_PRINTFUNCNAME( Any_vsscanf, "Same as Any_sscanf" );

  va_start( ap, fmt );
  retVal = Any_vsscanf( str, fmt, ap );
  va_end( ap );

  if( retVal > 0 )
  {
    ANY_LOG( 0, "Any_vsscanf returns [%d]", ANY_LOG_INFO, retVal );
  }
  else
  {
    ANY_LOG( 0, "Warning: Any_vsscanf returns %d value",
             ANY_LOG_WARNING, retVal );
  }

}

/*-------------------------------------------------------------------------*/
/* Memory functions                                                        */
/*-------------------------------------------------------------------------*/
bool test_memcmp( unsigned char *buff1, unsigned char *buff2 )
{
  char buff[EXAMPLE_BUFFLEN];
  int retVal;

  sprintf( buff, "Compare the buffer [%s] with the buffer [%s]",
           buff1, buff2 );
  EXAMPLE_PRINTFUNCNAME( Any_memcmp, buff );

  retVal = Any_memcmp( buff1, buff2, EXAMPLE_BUFFLEN_SHORT );

  ANY_LOG( 0, "Any_memcmp returns [%d]", ANY_LOG_INFO, retVal );

  return true;

}

bool test_memcpy( unsigned char *buff1, unsigned char *buff2 )
{
  unsigned char buff[EXAMPLE_BUFFLEN];
  unsigned char *result;
  bool retVal;

  sprintf( (char*)buff, "Copy the buffer [%s] into a temporary buffer",
           (char*)buff1 );
  EXAMPLE_PRINTFUNCNAME( Any_memcpy, buff );

  Any_memset( buff, 0, EXAMPLE_BUFFLEN );
  result = Any_memcpy( buff, buff1, EXAMPLE_BUFFLEN_SHORT );

  ANY_LOG( 0, "Any_memcpy returns [%s]", ANY_LOG_INFO, result );

  retVal = ( !memcmp( result, buff1, EXAMPLE_BUFFLEN_SHORT ) ) ? true : false;

  return retVal;

}

bool test_memmove( unsigned char *buff1, unsigned char *buff2 )
{
  unsigned char buff[EXAMPLE_BUFFLEN];
  unsigned char *result;
  bool retVal;

  sprintf( (char*)buff, "Move the buffer [%s] into a temporary buffer",
           (char*)buff1 );
  EXAMPLE_PRINTFUNCNAME( Any_memmove, buff );

  Any_memset( buff, 0, EXAMPLE_BUFFLEN );
  result = Any_memmove( buff, buff1, EXAMPLE_BUFFLEN_SHORT );

  ANY_LOG( 0, "Any_memmove returns [%s]", ANY_LOG_INFO, result );

  retVal = ( !memcmp( result, buff1, EXAMPLE_BUFFLEN_SHORT ) ) ? true : false;

  return retVal;
}

bool test_memchr( unsigned char *buff1, unsigned char *buff2 )
{
  char buff[EXAMPLE_BUFFLEN];
  unsigned char *retVal;

  sprintf( buff, "Find first occurrence of first byte of buffer"
           " [%s] into initial bytes of buffer [%s]",
           buff2, buff1 );

  EXAMPLE_PRINTFUNCNAME( Any_memchr, buff );

  retVal = Any_memchr( buff1, buff2[0], EXAMPLE_BUFFLEN_SHORT );

  if( retVal != NULL )
  {
    ANY_LOG( 0, "Any_memchr returns [%s]", ANY_LOG_INFO, retVal );
  }

  return true;
}

bool test_memmem( unsigned char *buff1, unsigned char *buff2 )
{
  char buff[EXAMPLE_BUFFLEN];
  void *retVal;

  sprintf( (char*)buff, "Find first occurrence of first three bytes of buffer"
           " [%s] into buffer [%s]",
           (char*)buff2, (char*)buff1 );

  EXAMPLE_PRINTFUNCNAME( Any_memmem, buff );

  retVal = Any_memmem( (const void*)buff1, EXAMPLE_BUFFLEN_SHORT,
                       (const void*)buff2, EXAMPLE_N );

  if( retVal != NULL )
  {
    ANY_LOG( 0, "Any_memmem returns [%s]", ANY_LOG_INFO, (char*)retVal );
  }

  return true;
}

bool test_memset( unsigned char *buff1, unsigned char *buff2 )
{
  char buff[EXAMPLE_BUFFLEN];
  unsigned char *retVal;

  sprintf( buff, "Reset the buffer [%s] (fill it with zeros)",
           buff1 );
  EXAMPLE_PRINTFUNCNAME( Any_memset, buff );

  retVal = Any_memset( buff1, 0, EXAMPLE_BUFFLEN_SHORT );

  ANY_LOG( 0, "Any_memset returns [%s]", ANY_LOG_INFO, retVal );

  return ( !retVal ) ? true : false;

}

/*-------------------------------------------------------------------------*/
/* Types definition and global variables                                   */
/*-------------------------------------------------------------------------*/
typedef bool(*ExampleStrFunc)(char*, char*);
typedef bool(*ExampleStrFmtFunc)(char*, char*);
typedef bool(*ExampleMemFunc)(unsigned char*, unsigned char*);

ExampleStrFunc strFuncs[] = { test_strcmp,
                              test_strncmp,
                              test_strcasecmp,
                              test_strncasecmp,
                              test_strcat,
                              test_strncat,
                              test_strchr,
                              test_strrchr,
                              test_strstr,
                              test_strlen,
                              test_strnlen,
                              test_strcpy,
                              test_strncpy,
                              test_strcoll,
                              test_strspn,
                              test_strcspn,
                              test_strtok,
                              test_strtok_r,
                              test_strsep,
                              test_strdup };

ExampleStrFmtFunc strFmtFuncs[] = { test_printf,
                                    test_fprintf,
                                    test_sprintf,
                                    test_snprintf,
                                    test_scanf,
                                    test_fscanf,
                                    test_sscanf };

ExampleMemFunc memFuncs[] = { test_memcmp,
                              test_memcpy,
                              test_memmove,
                              test_memchr,
                              test_memmem,
                              test_memset };

int main( int argc, char *argv[] )
{

  unsigned char buff1[EXAMPLE_BUFFLEN_SHORT];
  unsigned char buff2[EXAMPLE_BUFFLEN_SHORT];
  bool retVal;
  int i;

  printf( "################ STRING FUNCTIONS ################\n\n"
          "Use string [%s] and [%s]\n\n", EXAMPLE_STR1, EXAMPLE_STR2 );

  for( i=0; i< (int)( sizeof(strFuncs) / sizeof(ExampleStrFunc)); i++ )
  {
    strcpy( (char*)buff1, EXAMPLE_STR1 );
    strcpy( (char*)buff2, EXAMPLE_STR2 );
    retVal = (*strFuncs[i])( (char*)buff1, (char*)buff2 );
    printf( "\n" );
    if( !retVal )
    {
      ANY_LOG( 0, "Warning: last test returns unexpected values. Exit...",
               ANY_LOG_ERROR );
      exit(1);
    }
  }

  printf( "############# STRING FORMAT FUNCTIONS ############\n\n" );
  for( i=0; i<(int)( sizeof(strFmtFuncs) / sizeof(ExampleStrFmtFunc)); i++ )
  {
    strcpy( (char*)buff1, EXAMPLE_STR1 );
    strcpy( (char*)buff2, EXAMPLE_STR2 );
    retVal = (*strFmtFuncs[i])( (char*)buff1, (char*)buff2 );
    printf( "\n" );
    if( !retVal )
    {
      ANY_LOG( 0, "Warning: last test returns unexpected values. Exit...",
               ANY_LOG_ERROR );
      exit(1);
    }
  }

  printf( "############# VA_LIST STRING FUNCTIONS ############\n\n" );
  strcpy( (char*)buff1, EXAMPLE_STR1 );
  strcpy( (char*)buff2, EXAMPLE_STR2 );
  test_vsprintf( (char*)buff1, "%s", buff2  );
  printf( "\n" );

  strcpy( (char*)buff1, EXAMPLE_STR1 );
  strcpy( (char*)buff2, EXAMPLE_STR2 );
  test_vsnprintf( (char*)buff1, "%s", buff2  );
  printf( "\n" );

  strcpy( (char*)buff1, EXAMPLE_STR1 );
  strcpy( (char*)buff2, EXAMPLE_STR2 );
  test_vsscanf( (char*)buff1, "%s", buff2  );
  printf( "\n" );

  srand( (long)time(NULL) );
  for( i=0; i<EXAMPLE_BUFFLEN_SHORT-1; i++ )
  {
    buff1[i] = 32+(char)(rand() % 94);
    buff2[i] = 32+(char)(rand() % 94);
  }
  buff1[EXAMPLE_BUFFLEN_SHORT-1] = 0;
  buff2[EXAMPLE_BUFFLEN_SHORT-1] = 0;

  Any_printf( "################ MEMORY FUNCTIONS ################\n\n" );
  Any_printf( "Use random generated buffers [%s] and [%s]\n\n", buff1, buff2 );
  for( i=0; i<(int)( sizeof(memFuncs) / sizeof(ExampleMemFunc)); i++ )
  {
    (*memFuncs[i])( buff1, buff2 );
    printf( "\n" );
  }

  return 0;

}


/* EOF */
