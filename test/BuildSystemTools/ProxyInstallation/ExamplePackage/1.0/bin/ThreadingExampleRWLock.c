/*
 *  Example of RWLock usage
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
 *  Description: This example allocate a thread pool and synchronize them 
 *               using RWLock primitives
 *
 */


#include <stdio.h>
#include <string.h>

#include <Any.h>
#include <Threads.h>
#include <RWLock.h>


static void *MyThread_threadMain( void *instance )
{
  RWLock *rwlock = (RWLock*)instance;
  int status = 0;
  int secs = 0;

  secs = rand() % 10;

  ANY_LOG( 0, "Sleeping %d seconds before RWLock_readLock()",
           ANY_LOG_INFO, secs );

  Any_sleepSeconds( secs );

  status = RWLock_readLock( rwlock );
  ANY_REQUIRE( status == 0 );

  secs = rand() % 10;

  ANY_LOG( 0, "Grabbing the reading lock for %d seconds",
           ANY_LOG_INFO, secs );

  Any_sleepSeconds( secs );

  status = RWLock_unlock( rwlock );
  ANY_REQUIRE( status == 0 );

  ANY_LOG( 0, "Releasing the reading lock", ANY_LOG_INFO );

  return( NULL );
}


int main( int argc, char *argv[] )
{
  Threads *pool = (Threads*)NULL;
  int nthreads = 0;
  int status = 0;
  int secs = 0;
  int i = 0;
  RWLock rwlock;

  ANY_LOG( 0, "Starting Test ...", ANY_LOG_INFO );

  ANY_LOG( 0, "Initializing rwlock", ANY_LOG_INFO );

  if ( RWLock_init( &rwlock, RWLOCK_PRIVATE ) == false )
  {
    ANY_LOG( 0, "Unable to initialize the rwlock", ANY_LOG_FATAL );
    exit( 1 );
  }

  nthreads = rand() % 10;

  ANY_LOG( 0, "Allocating space for %d threads", ANY_LOG_INFO, nthreads );

  pool = ANY_NTALLOC( nthreads, Threads );
  ANY_REQUIRE( pool );

  for ( i = 0; i < nthreads; i++ )
  {
    ANY_LOG( 0, "Initializing thread%d", ANY_LOG_INFO, i );

    if ( Threads_init( &pool[i], false ) == false )
    {
      ANY_LOG( 0, "Unable to initialize thread%d", ANY_LOG_FATAL, i );
      exit( 1 );
    }
  }

  secs = rand() % 10;

  ANY_LOG( 0, "Main grabs the writing lock for %d seconds",
           ANY_LOG_INFO, secs );

  status = RWLock_writeLock( &rwlock );
  ANY_REQUIRE( status == 0 );

  for ( i = 0; i < nthreads; i++ )
  {
    ANY_LOG( 0, "Starting thread%d", ANY_LOG_INFO, i );

    status = Threads_start( &pool[i], MyThread_threadMain, (void*)&rwlock );
    ANY_REQUIRE( status == 0 );
  }

  Any_sleepSeconds( secs );

  status = RWLock_unlock( &rwlock );
  ANY_REQUIRE( status == 0 );

  ANY_LOG( 0, "Releasing the writing lock", ANY_LOG_INFO );

  Any_sleepSeconds( 10 );

  for ( i = 0; i < nthreads; i++ )
  {
    ANY_LOG( 0, "Clearing thread%d", ANY_LOG_INFO, i );
    Threads_clear( &pool[i] );
  }

  ANY_LOG( 0, "Clearing rwlock", ANY_LOG_INFO );

  RWLock_clear( &rwlock );

  ANY_FREE( pool );

  ANY_LOG( 0, "Test terminated!!!", ANY_LOG_INFO );

  return( 0 );
}


/* EOF */
