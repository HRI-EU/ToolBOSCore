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


#include <stdlib.h>

#include <Any.h>
#include <Atomic.h>
#include <Cond.h>
#include <MThreadKey.h>
#include <RWLock.h>
#include <Threads.h>

#include <CuTest.h>


/*---------------------------------------------------------------------------*/
/* MTList                                                                    */
/*---------------------------------------------------------------------------*/


void Test_AtomicOperations( CuTest *tc )
{
    AnyAtomic i = -1;
    AnyAtomic64 ll = -1;

    Atomic_set( &i, 0 );

    Atomic64_set( &ll, 0 );

    CuAssertTrue( tc, Atomic_get( &i ) == 0 );

    CuAssertTrue( tc, Atomic64_get( &ll ) == 0 );

    ANY_TRACE( 3, "%ld", i );
    ANY_TRACE( 3, "%lld", (long long)ll );

    Atomic_inc( &i );

    Atomic64_inc( &ll );

    ANY_TRACE( 3, "%ld", i );

    ANY_TRACE( 3, "%lld", (long long)ll );
}


/*---------------------------------------------------------------------------*/
/* Conditions                                                                */
/*---------------------------------------------------------------------------*/


void Test_Condition( CuTest *tc )
{
    Cond *cond;

    cond = Cond_new();
    CuAssertPtrNotNull( tc, cond );

    Cond_init( cond, COND_PRIVATE );
    Cond_wait( cond, 1000000 );

    Cond_clear( cond );
    Cond_delete( cond );
}


/*---------------------------------------------------------------------------*/
/* MThreadKey                                                                */
/*---------------------------------------------------------------------------*/


void Test_MThreadKey( CuTest *tc )
{
    MThreadKey *key = NULL;

    key = MThreadKey_new();
    CuAssertPtrNotNull( tc, key );

    CuAssertTrue( tc, MThreadKey_init( key, NULL ));

    ANY_LOG( 3, "Setting the user's value", ANY_LOG_INFO );
    CuAssertTrue( tc, MThreadKey_set( key, key ));

    CuAssertTrue( tc, MThreadKey_get( key ) == (void *)key );

    MThreadKey_clear( key );
    MThreadKey_delete( key );
}


/*---------------------------------------------------------------------------*/
/* RWLock                                                                    */
/*---------------------------------------------------------------------------*/


void *MyThread_threadMain( void *instance )
{
    RWLock *rwlock = (RWLock *)instance;
    int status = 0;
    int secs = 0;

    secs = rand() % 4;

    ANY_LOG( 3, "Sleeping %d seconds before RWLock_readLock()",
             ANY_LOG_INFO, secs );

    Any_sleepSeconds( secs );

    status = RWLock_readLock( rwlock );
    ANY_REQUIRE( status == 0 );

    secs = rand() % 4;

    ANY_LOG( 3, "Grabbing the reading lock for %d seconds",
             ANY_LOG_INFO, secs );

    Any_sleepSeconds( secs );

    status = RWLock_unlock( rwlock );
    ANY_REQUIRE( status == 0 );

    ANY_LOG( 3, "Releasing the reading lock", ANY_LOG_INFO );

    return ( 0 );
}


void Test_RWLock( CuTest *tc )
{
    Threads *pool = (Threads *)NULL;
    int nthreads = 0;
    int status = 0;
    int secs = 0;
    int i = 0;
    RWLock *rwlock = (RWLock *)NULL;

    ANY_LOG( 3, "Initializing rwlock", ANY_LOG_INFO );

    rwlock = RWLock_new();
    CuAssertPtrNotNull( tc, rwlock );
    CuAssertTrue( tc, RWLock_init( rwlock, RWLOCK_PRIVATE ));

    nthreads = rand() % 10;
    ANY_LOG( 3, "Allocating space for %d threads", ANY_LOG_INFO, nthreads );

    pool = ANY_NTALLOC( nthreads, Threads );
    CuAssertPtrNotNull( tc, pool );

    for( i = 0; i < nthreads; i++ )
    {
        ANY_LOG( 3, "Initializing thread%d", ANY_LOG_INFO, i );
        CuAssertTrue( tc, Threads_init( &pool[ i ], true ));
    }

    secs = rand() % 4;

    ANY_LOG( 3, "Main grabs the writing lock for %d seconds",
             ANY_LOG_INFO, secs );

    status = RWLock_writeLock( rwlock );
    ANY_REQUIRE( status == 0 );

    for( i = 0; i < nthreads; i++ )
    {
        ANY_LOG( 3, "Starting thread%d", ANY_LOG_INFO, i );

        status = Threads_start( &pool[ i ], MyThread_threadMain, (void *)rwlock );
        ANY_REQUIRE( status == 0 );
    }

    Any_sleepSeconds( secs );

    status = RWLock_unlock( rwlock );
    ANY_REQUIRE( status == 0 );

    ANY_LOG( 3, "Releasing the writing lock", ANY_LOG_INFO );

    Any_sleepSeconds( 2 );

    for( i = 0; i < nthreads; i++ )
    {
        Threads_join( &pool[ i ], NULL );

        ANY_LOG( 3, "Clearing thread%d", ANY_LOG_INFO, i );
        Threads_clear( &pool[ i ] );
    }

    ANY_LOG( 3, "Clearing rwlock", ANY_LOG_INFO );
    RWLock_clear( rwlock );
    RWLock_delete( rwlock );

    ANY_FREE( pool );
}


/*---------------------------------------------------------------------------*/
/* Setting thread priority                                                   */
/*---------------------------------------------------------------------------*/


void Test_setPriority( CuTest *tc )
{
    Threads *t;

    t = Threads_new();
    CuAssertPtrNotNull( tc, t );
    Threads_init( t, true );


//     DOES NOT WORK, YET:
//
//     ANY_LOG( 0, "You should get a Warning afterwards", ANY_LOG_INFO );
//     Threads_setPriority( t, 10 );

    Threads_clear( t );
    Threads_delete( t );
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

    SUITE_ADD_TEST( suite, Test_AtomicOperations );

    SUITE_ADD_TEST( suite, Test_Condition );
    SUITE_ADD_TEST( suite, Test_MThreadKey );
    SUITE_ADD_TEST( suite, Test_RWLock );
    SUITE_ADD_TEST( suite, Test_setPriority );

    CuSuiteRun( suite );
    CuSuiteSummary( suite, output );
    CuSuiteDetails( suite, output );

    Any_fprintf( stderr, "%s\n", output->buffer );

    CuSuiteDelete( suite );
    CuStringDelete( output );

    return suite->failCount;
}


/* EOF */
