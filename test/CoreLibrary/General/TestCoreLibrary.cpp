/*
 *  Unittests for essential macros and functions in ToolBOS core library
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


/*---------------------------------------------------------------------------*/
/* Includes                                                                  */
/*---------------------------------------------------------------------------*/


#include <stdio.h>
#include <stdlib.h>

#include <Any.h>
#include <Base.h>
#include <BBCM-C.h>
#include <BerkeleySocket.h>
#include <DynamicLoader.h>
#include <FileSystem.h>
#include <RTTimer.h>

#include <CuTest.h>


/*---------------------------------------------------------------------------*/
/* ANY_* macros and functions                                                */
/*---------------------------------------------------------------------------*/


void Test_ANY_LOG( CuTest *tc )
{
    unsigned int i = 0;
    BaseUI64 evenLonger = 123456789;

    ANY_REQUIRE( tc );

    for( i = 0; i < 10; i++ )
    {
        ANY_LOG( 3, "Hello World! (i=%d)", ANY_LOG_INFO, i );
        ANY_LOG_ONCE( 3, "Hello World! [should appear only once]", ANY_LOG_INFO );
    }

    Any_setShortLogFormat();
    ANY_LOG( 3, "%"
            BASEUI64_FORMAT, ANY_LOG_INFO, evenLonger );
    Any_setLongLogFormat();

    if( Any_getDebugLevel() >= 3 )
    {
#if defined(__MSVC__)
        /* temporarily disabled
        std::cout << "Example: %" BASEUI64_FORMAT << std::endl;
        */
#endif
    }
}


void Test_ANY_REQUIRE_callback( void *args )
{
    /* In the unittest the ANY_REQUIRE should pass (cond is true).
     * If it doesn't this function will be executed, making the test fail.
     */
    CuFail((CuTest *)args, "Test should not enter this callback function" );
}


void Test_ANY_REQUIRE( CuTest *tc )
{
    unsigned x = 5;
    unsigned y = 2;
    unsigned sum = 10;

    ANY_REQUIRE( tc );

    Any_onRequire( Test_ANY_REQUIRE_callback, tc );

    ANY_REQUIRE( x * y == sum );
    CuAssertTrue( tc, x * y == sum );

    ANY_REQUIRE_MSG( sum - x - x == 0, "Test failed" );

    ANY_REQUIRE_VMSG( x + y + 3 == sum, "Test failed, sum=%d expected", sum );
}


void Test_ANY_WHERE( CuTest *tc )
{
    ANY_REQUIRE( tc );

    ANY_WHERE( 3 );
}


void Test_Any_isLittleEndian( CuTest *tc )
{
    ANY_REQUIRE( tc );

    if( ANY_ISLITTLEENDIAN)
    {
        ANY_LOG( 3, "This system is LITTLE endian.", ANY_LOG_INFO );
    }
    else
    {
        ANY_LOG( 3, "This system is BIG endian.", ANY_LOG_INFO );
    }

    CuAssertTrue( tc, Any_isLittleEndian());
}


void Test_Any_free( CuTest *tc )
{
    int *x = (int *)NULL;

    ANY_REQUIRE( tc );

    x = ANY_TALLOC( int );
    ANY_REQUIRE( x );

    *x = 123;

    ANY_TRACE( 3, "%d", *x );

    /* free the memory and set to NULL */
    ANY_FREE_SET( x );

    /* freeing again should not harm */
    ANY_FREE_SET( x );
}


void Test_Any_sleepMilliSeconds( CuTest *tc )
{
    ANY_REQUIRE( tc );

    ANY_LOG( 3, "waiting 100 ms...", ANY_LOG_INFO );
    Any_sleepMilliSeconds( 100 );
}


void Test_Any_snprintf( CuTest *tc )
{
#define EXAMPLE_BUFLEN ( 20 )
    char buffer[EXAMPLE_BUFLEN] = "";

    ANY_REQUIRE( tc );

    Any_snprintf( buffer, EXAMPLE_BUFLEN - 1, "Hello %s", "World" );
    ANY_TRACE( 3, "%s", buffer );

    CuAssertTrue( tc, Any_strncmp( buffer, "Hello World", EXAMPLE_BUFLEN - 1 ) == 0 );

#undef EXAMPLE_BUFLEN
}


/*---------------------------------------------------------------------------*/
/* BBCM helpers                                                              */
/*---------------------------------------------------------------------------*/


typedef struct TestBBCM
{
    char instanceName[BBCM_MAXINSTANCENAMELEN];

} TestBBCM;


void Test_BBCM_LOG( CuTest *tc )
{
    TestBBCM t;

    ANY_REQUIRE( tc );

    Any_strncpy( t.instanceName, "myInstance", BBCM_MAXINSTANCENAMELEN - 1 );

    BBCM_MSG( &t, 3, "Hello World!", BBCM_LOG_INFO );
    BBCM_LOG( &t, 3, "%s", BBCM_LOG_INFO, "Hello World!" );
    BBCM_LOG( &t, 3, "%d + %d = %d", BBCM_LOG_INFO, 1, 2, 3 );
}


/*---------------------------------------------------------------------------*/
/* Berkeley Socket                                                           */
/*---------------------------------------------------------------------------*/


#define HOSTNAME ( "www.kernel.org" )


void Test_BerkeleySocket_host2Addr( CuTest *tc )
{
    char ipv4Address[16];

    ANY_REQUIRE( tc );

    BerkeleySocket_host2Addr(HOSTNAME, ipv4Address, 16 );
    ANY_LOG( 3, "IPv4 address of %s is: %s", ANY_LOG_INFO, HOSTNAME, ipv4Address );
}


#undef HOSTNAME


void Test_BerkeleySocket_showTimeouts( CuTest *tc )
{
    BerkeleySocket *socket = (BerkeleySocket *)NULL;

    ANY_REQUIRE( tc );

    socket = BerkeleySocket_new();
    ANY_REQUIRE( socket );

    BerkeleySocket_init( socket );
    BerkeleySocket_setDefaultTimeout( socket, BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ));

    ANY_TRACE( 3, "%ld sec", BerkeleySocket_getConnectTimeout( socket ) / 1000000 );
    ANY_TRACE( 3, "%ld sec", BerkeleySocket_getIsReadPossibleTimeout( socket ) / 1000000 );
    ANY_TRACE( 3, "%ld sec", BerkeleySocket_getIsWritePossibleTimeout( socket ) / 1000000 );
    ANY_TRACE( 3, "%d sec", BerkeleySocket_getLingerTimeout( socket ) / 1000000 );

    BerkeleySocket_clear( socket );
    BerkeleySocket_delete( socket );
}


/*---------------------------------------------------------------------------*/
/* Dynamic Loader                                                            */
/*---------------------------------------------------------------------------*/


#define FUNCTIONNAME "Global_function"


void Global_function( const char *str )
{
    ANY_REQUIRE_MSG( str, "The str parameter must be valid" );

    ANY_LOG( 3, "I was called by a pointer to function with the parameter '%s'", ANY_LOG_INFO, str );
}


void Test_DynamicLoader( CuTest *tc )
{
    DynamicLoaderFunction function = NULL;
    DynamicLoader *dl = NULL;

    ANY_REQUIRE( tc );

    ANY_LOG( 3, "Searching the symbol '%s' globally using directly the DynamicLoader_getSymbolByName()", ANY_LOG_INFO,
             FUNCTIONNAME );

    function = DynamicLoader_getFunctionSymbol( NULL, FUNCTIONNAME );

    if( function )
    {
        void (*callFunc)( const char * ) = (void ( * )( const char * ))function;

        ANY_LOG( 3, "Calling the function '%s'", ANY_LOG_INFO, FUNCTIONNAME );

        ( *callFunc )( "It works :-)" );
    }
    else
    {
        char *err = DynamicLoader_getError( dl );

        ANY_LOG( 3, "The function '%s' hasn't been found. The error is: %s", ANY_LOG_INFO, FUNCTIONNAME, err );
    }

    ANY_LOG( 3, "Allocating a new DynamicLoader instance", ANY_LOG_INFO );
    dl = DynamicLoader_new();
    ANY_REQUIRE( dl );

    DynamicLoader_init( dl, NULL );

    ANY_LOG( 3, "Searching the symbol '%s' globally using a DynamicLoader instance", ANY_LOG_INFO, FUNCTIONNAME );
    function = DynamicLoader_getFunctionSymbol( dl, FUNCTIONNAME );

    if( function )
    {
        void (*callFunc)( const char * ) = (void ( * )( const char * ))function;

        ANY_LOG( 3, "Calling the function '%s'", ANY_LOG_INFO, FUNCTIONNAME );

        ( *callFunc )( "It works :-)" );
    }
    else
    {
        char *err = DynamicLoader_getError( dl );

        ANY_LOG( 3, "The function '%s' hasn't been found. The error is: %s", ANY_LOG_INFO, FUNCTIONNAME, err );
    }

    DynamicLoader_clear( dl );
    DynamicLoader_delete( dl );
}


/*---------------------------------------------------------------------------*/
/* FileSystem                                                                */
/*---------------------------------------------------------------------------*/


void Test_FileSystem_makeDirectories( CuTest *tc )
{
    /* Windows does not have the more secure mkdtemp() function */

#if defined(__msvc__)
    BaseBool status   = false;
    char path1[ 128 ] = "";
    char path2[ 128 ] = "";
    char path3[ 128 ] = "";
    char *tmp = tempnam( NULL, "test-" );
#else
    BaseBool status = false;
    char path1[128] = "";
    char path2[128] = "";
    char path3[128] = "";
    char pattern[12] = "test-XXXXXX";
    char *tmp = (char *)NULL;

    tmp = mkdtemp( pattern );
#endif

    ANY_REQUIRE( tc );

    ANY_REQUIRE_VMSG( tmp, "tempdir=%s", tmp );

    Any_snprintf( path1, 127, "%s/foo/bar/baz", tmp );          /* absolute */
    Any_snprintf( path2, 127, "%s/foo/bar/baz/blubb", tmp );    /* absolute */
    Any_snprintf( path3, 127, "build/test%s", tmp );           /* relative */


    /* try to create a completely new directory tree */
    status = FileSystem_makeDirectories( path1 );
    CuAssertTrue( tc, status );
    CuAssertTrue( tc, FileSystem_isDirectory( path1 ));

    /* then add another directory into an existing dir. tree */
    status = FileSystem_makeDirectories( path2 );
    CuAssertTrue( tc, status );
    CuAssertTrue( tc, FileSystem_isDirectory( path2 ));

    /* create a directory tree relative to CWD */
    status = FileSystem_makeDirectories( path3 );
    CuAssertTrue( tc, status );
    CuAssertTrue( tc, FileSystem_isDirectory( path3 ));

    /* should not be a problem to create a directory twice */
    status = FileSystem_makeDirectories( path3 );
    CuAssertTrue( tc, status );
    CuAssertTrue( tc, FileSystem_isDirectory( path3 ));


    /* clean-up */
    FileSystem_remove( tmp );                   /* contains path1 and path2 */
    FileSystem_remove( path3 );
}


/*---------------------------------------------------------------------------*/
/* RTTimer                                                                   */
/*---------------------------------------------------------------------------*/


void Test_RTTimer( CuTest *tc )
{
    RTTimer *myTimer = (RTTimer *)NULL;
    RTTimerSpec spec;
    unsigned long long elapsed = 0;
    unsigned long long minTime = 0;
    unsigned long long averangeTime = 0;
    unsigned long long maxTime = 0;
    unsigned long long counter = 0;
    unsigned long long totalTime = 0;

    ANY_REQUIRE( tc );

    myTimer = RTTimer_new();
    ANY_REQUIRE( myTimer );

    CuAssertTrue( tc, RTTimer_init( myTimer ));

    ANY_LOG( 3, "Start empty measure", ANY_LOG_INFO );
    RTTimer_start( myTimer );

    Any_sleepMilliSeconds( 100 );

    /* empty execution */
    RTTimer_stop( myTimer );

    ANY_LOG( 3, "End empty measure", ANY_LOG_INFO );

    /* grabs some statistics */
    elapsed = RTTimer_getElapsed( myTimer );
    minTime = RTTimer_getMinTime( myTimer );
    averangeTime = RTTimer_getAverageTime( myTimer );
    maxTime = RTTimer_getMaxTime( myTimer );
    totalTime = RTTimer_getTotalTime( myTimer );
    RTTimer_getTotalTimeExt( myTimer, &spec );
    counter = RTTimer_getCount( myTimer );

    ANY_LOG( 5, "Elapsed start/stop time is %llu microsecs",
             ANY_LOG_INFO, elapsed );
    ANY_LOG( 5, "Min start/stop time is %llu microsecs",
             ANY_LOG_INFO, minTime );
    ANY_LOG( 5, "Average start/stop time is %llu microsecs",
             ANY_LOG_INFO, averangeTime );
    ANY_LOG( 5, "Max start/stop time is %llu microsecs",
             ANY_LOG_INFO, maxTime );
    ANY_LOG( 5, "Total start/stop time is %llu secs (%lu days %lu:%lu:%lu.%06lu)",
             ANY_LOG_INFO, totalTime, spec.day, spec.hour, spec.minute, spec.second, spec.microsecond );
    ANY_LOG( 5, "Total start/stop counter is %llu",
             ANY_LOG_INFO, counter );

    RTTimer_clear( myTimer );
    RTTimer_delete( myTimer );
}


/*---------------------------------------------------------------------------*/
/* Datatypes + lifecycle                                                     */
/*---------------------------------------------------------------------------*/


void Test_BaseTypes( CuTest *tc )
{
    BaseBool baseBool = false;
    BaseI8 baseI8 = 10;
    BaseUI32 ui32max = BASEUI32_MAX;
    BaseI32 i32max = BASEI32_MAX;
    BaseI64 i64max = BASEI64_MAX;
    BaseF64 f64 = 0.00;
    size_t s = 123456;

    ANY_REQUIRE( tc );

    Any_sscanf( "1234567890.12345", "%"
            BASEF64_SCAN, &f64 );

    ANY_TRACE( 3, "%s", ( baseBool ? "true" : "false" ));
    ANY_TRACE( 3, "%d", (int)baseI8 );

    ANY_TRACE( 3, "%"
            BASEUI32_PRINT, ui32max );
    ANY_TRACE( 3, "%"
            BASEI32_PRINT, i32max );
    ANY_TRACE( 3, "%"
            BASEI64_PRINT, i64max );
    ANY_TRACE( 3, "%"
            SIZE_PRINT, s );
    ANY_TRACE( 3, "%"
            BASEF64_PRINT, f64 );

    CuAssertTrue( tc, f64 > 1234567890.12 );
    CuAssertTrue( tc, f64 < 1234567890.99 );
}


void Test_Base_flipEndian( CuTest *tc )
{
    BaseUI32 i = 2343323;
    BaseF64 f = 6345.43453;

    ANY_REQUIRE( tc );

    ANY_LOG( 3, "Flip int: %"
            BASEUI32_PRINT
            " %"
            BASEUI32_PRINT
            " %"
            BASEUI32_PRINT,
             ANY_LOG_INFO, i, BASEUI32_FLIPENDIAN( i ),
             BASEUI32_FLIPENDIAN( BASEUI32_FLIPENDIAN( i )));

    ANY_LOG( 3, "Flip double: %"
            BASEF64_PRINT
            " %"
            BASEF64_PRINT
            " %"
            BASEF64_PRINT,
             ANY_LOG_INFO, f, BASEF64_FLIPENDIAN( f ),
             BASEF64_FLIPENDIAN( BASEF64_FLIPENDIAN( f )));
}


void Test_MemI8_lifecycle( CuTest *tc )
{
    MemI8 *data = (MemI8 *)NULL;

    ANY_REQUIRE( tc );

    data = MemI8_new();
    CuAssertTrue( tc, data != (MemI8 *)NULL );

    MemI8_init( data, 100 );
    CuAssertIntEquals( tc, 100, MemI8_getLength( data ));

    MemI8_clear( data );
    CuAssertIntEquals( tc, 0, MemI8_getLength( data ));
    CuAssertPtrEquals( tc, 0, data->buffer );

    MemI8_delete( data );
}


void Test_MemI8_toString( CuTest *tc )
{
    BaseI8 *s = (BaseI8 *)NULL;
    MemI8 *data = (MemI8 *)NULL;

    ANY_REQUIRE( tc );

    data = MemI8_new();
    MemI8_init( data, 100 );

    s = MemI8_getBuffer( data );
    CuAssertPtrNotNull( tc, s );

    CuAssertIntEquals( tc, 0, Any_strcmp((const char *)s, "" ));

    Any_snprintf((char *)s, 99, "Hello, World!" );
    CuAssertIntEquals( tc, 0, Any_strcmp((const char *)data->buffer,
                                         "Hello, World!" ));

    MemI8_clear( data );
    MemI8_delete( data );
}


void Test_MemI8_copyOnHeap( CuTest *tc )
{
    MemI8 *hello = (MemI8 *)NULL;
    MemI8 *world = (MemI8 *)NULL;
    MemI8 *foo = (MemI8 *)NULL;
    int result = 0;

    ANY_REQUIRE( tc );

    hello = MemI8_new();
    MemI8_init( hello, 20 );
    Any_strncpy((char *)MemI8_getBuffer( hello ), "Hello", 19 );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( hello ));

    world = MemI8_new();
    MemI8_init( world, 20 );
    Any_strncpy((char *)MemI8_getBuffer( world ), "World", 19 );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( world ));

    result = MemI8_copy( world, hello );
    ANY_TRACE( 3, "%d", result );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( world ));
    CuAssertIntEquals( tc, 0, result );

    foo = MemI8_new();
    MemI8_init( foo, 5 );
    Any_strncpy((char *)MemI8_getBuffer( foo ), "Foo", 4 );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( foo ));

    /* 'World' does not fit into 'Foo' buffer, so expect to return -1 */
    result = MemI8_copy( foo, world );
    ANY_TRACE( 3, "%d", result );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( foo ));
    CuAssertIntEquals( tc, -1, result );

    MemI8_clear( hello );
    MemI8_delete( hello );

    MemI8_clear( foo );
    MemI8_delete( foo );

    MemI8_clear( world );
    MemI8_delete( world );
}


void Test_MemI8_copyOnStack( CuTest *tc )
{
    MemI8 hello;
    MemI8 world;
    MemI8 foo;
    int result = 0;

    ANY_REQUIRE( tc );

    MemI8_init( &hello, 20 );
    Any_strncpy((char *)MemI8_getBuffer( &hello ), "Hello", 19 );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( &hello ));

    MemI8_init( &world, 20 );
    Any_strncpy((char *)MemI8_getBuffer( &world ), "World", 19 );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( &world ));

    ANY_LOG( 3, "calling MemI8_copy( &world, &hello );", ANY_LOG_INFO );
    result = MemI8_copy( &world, &hello );
    ANY_TRACE( 3, "%d", result );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( &world ));
    CuAssertIntEquals( tc, 0, result );

    MemI8_init( &foo, 5 );
    Any_strncpy((char *)MemI8_getBuffer( &foo ), "Foo", 4 );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( &foo ));

    /* 'World' does not fit into 'Foo' buffer, so expect to return -1 */
    ANY_LOG( 3, "calling MemI8_copy( &foo, &world );", ANY_LOG_INFO );
    result = MemI8_copy( &foo, &world );
    ANY_TRACE( 3, "%d", result );
    ANY_TRACE( 3, "%s", MemI8_getBuffer( &foo ));
    CuAssertIntEquals( tc, -1, result );

    ANY_LOG( 3, "clearing foo", ANY_LOG_INFO );
    MemI8_clear( &foo );

    ANY_LOG( 3, "clearing world", ANY_LOG_INFO );
    MemI8_clear( &world );
}


void Test_MemI8_copyConstr( CuTest *tc )
{
#define MEM_LENGTH 100

    int i = 0;
    int status = 0;
    BaseI8 *ptr = (BaseI8 *)NULL;
    MemI8 *first = (MemI8 *)NULL;
    MemI8 *second = (MemI8 *)NULL;

    ANY_REQUIRE( tc );

    first = MemI8_new();
    CuAssertPtrNotNull( tc, first );

    status = MemI8_init( first, MEM_LENGTH );
    CuAssertTrue( tc, status == 0 );

    ptr = MemI8_getBuffer( first );
    CuAssertPtrNotNull( tc, ptr );

    for( i = 0; i < MEM_LENGTH; ++i )
    {
        ptr[ i ] = i;
    }


    // copy to another MemI8
    second = MemI8_new();
    CuAssertPtrNotNull( tc, second );
    MemI8_copyConstr( second, first );


    CuAssertTrue( tc, Any_strncmp((char *)MemI8_getBuffer( first ),
                                  (char *)MemI8_getBuffer( second ),
                                  MEM_LENGTH - 1 ) == 0 );

    MemI8_clear( first );
    MemI8_delete( first );

    MemI8_clear( second );
    MemI8_delete( second );

#undef MEM_LENGTH
}


/*---------------------------------------------------------------------------*/
/* Main program                                                              */
/*---------------------------------------------------------------------------*/


int main( void )
{
    CuSuite *suite = CuSuiteNew();
    CuString *output = CuStringNew();
    char *verbose = (char *)NULL;

    ANY_REQUIRE( suite );
    ANY_REQUIRE( output );

    verbose = getenv((char *)"VERBOSE" );
    if( verbose != NULL && Any_strcmp( verbose, (char *)"TRUE" ) == 0 )
    {
        Any_setDebugLevel( 10 );
    }
    else
    {
        Any_setDebugLevel( 1 );
    }

    SUITE_ADD_TEST( suite, Test_ANY_LOG );
    SUITE_ADD_TEST( suite, Test_ANY_REQUIRE );
    SUITE_ADD_TEST( suite, Test_ANY_WHERE );
    SUITE_ADD_TEST( suite, Test_Any_isLittleEndian );
    SUITE_ADD_TEST( suite, Test_Any_free );
    SUITE_ADD_TEST( suite, Test_Any_sleepMilliSeconds );
    SUITE_ADD_TEST( suite, Test_Any_snprintf );
    SUITE_ADD_TEST( suite, Test_BerkeleySocket_host2Addr );
    SUITE_ADD_TEST( suite, Test_BerkeleySocket_showTimeouts );
    SUITE_ADD_TEST( suite, Test_BBCM_LOG );
    SUITE_ADD_TEST( suite, Test_DynamicLoader );
    SUITE_ADD_TEST( suite, Test_FileSystem_makeDirectories );
    SUITE_ADD_TEST( suite, Test_RTTimer );

    CuSuiteRun( suite );
    CuSuiteSummary( suite, output );
    CuSuiteDetails( suite, output );

    Any_fprintf( stderr, "%s\n", output->buffer );

    CuSuiteDelete( suite );
    CuStringDelete( output );

    return suite->failCount;
}


/* EOF */
