/*
 *  Example of Threads_join() usage
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
 *  Description: This test run two joinable threads and terminate it upon request
 */


#include <stdio.h>
#include <string.h>

#include <Any.h>
#include <Base.h>
#include <Threads.h>
#include <Mutex.h>


/*!
 * \brief MyThread's flag status of not running
 *
 * It's used on MyThread.stat as status not running
 *
 */
#define MYTHREAD_NORUNNING    0x00000001

/*!
 * \brief MyThread's flag status of running
 *
 * It's used on MyThread.stat as status running
 *
 */
#define MYTHREAD_RUNNING    0x00000002

/*!
 * \brief MyThread's flag status of stopped
 *
 * It's used on MyThread.stat as status stopped
 *
 */
#define MYTHREAD_STOPPED    0x00000004

/*!
 * \brief MyThread's flag status of termination
 *
 * It's used on MyThread.stat as status termination
 *
 */
#define MYTHREAD_TERMINATE    0x00000008


void *MyThread_threadMain( void *instance );

/*!
 * \brief Thread's structure
 *
 */
typedef struct MyThread
{
  char *name;
  Mutex lock;
  Threads thread;
  int threadStatus;
} MyThread;


MyThread* MyThread_new( void )
{
  MyThread *self = (MyThread*)NULL;

  self = ANY_TALLOC( MyThread );
  ANY_REQUIRE( self );

  return( self );
}

bool MyThread_init( MyThread *self, char *name )
{
  ANY_REQUIRE( self );
  ANY_REQUIRE( name );

  self->name = (char*)ANY_BALLOC( strlen( name ) + 1 );
  ANY_REQUIRE( self->name );

  strcpy( self->name, name );

  self->threadStatus = MYTHREAD_NORUNNING;

  if ( Mutex_init( &self->lock, MUTEX_PRIVATE ) == false )
  {
    ANY_FREE( self->name );
    self->name = (char*)NULL;
    return( false );
  }

  /* initialize the thread */
  if ( Threads_init( &(self->thread), true ) == false )
  {
    ANY_FREE( self->name );
    self->name = (char*)NULL;

    Mutex_clear( &self->lock );

    return( false );
  }

  return( true );
}

int MyThread_getStatus( MyThread *self )
{
  int status = 0;
  int retval = 0;

  ANY_REQUIRE( self );

  status = Mutex_lock( &self->lock );
  ANY_REQUIRE( status == 0 );

  retval = self->threadStatus;

  status = Mutex_unlock( &self->lock );
  ANY_REQUIRE( status == 0 );

  return( retval );
}

void MyThread_setStatus( MyThread *self, int tstat )
{
  int status = 0;

  ANY_REQUIRE( self );

  status = Mutex_lock( &self->lock );
  ANY_REQUIRE( status == 0 );

  self->threadStatus = tstat;

  status = Mutex_unlock( &self->lock );
  ANY_REQUIRE( status == 0 );
}

bool MyThread_start( MyThread *self )
{
  int status = 0;

  ANY_REQUIRE( self );

  if ( !( MyThread_getStatus( self ) & MYTHREAD_RUNNING) )
  {
    /* start the thread */
    status = Threads_start( &(self->thread), MyThread_threadMain, (void*)self );

    /*
     * check the Threads_start() return status because only
     * here we know if the thread is started correctly
     */
    if ( status != 0 )
    {
      ANY_LOG( 0, "Not enough system resource for the thread", ANY_LOG_FATAL );
    }
  }

  return( status == 0 );
}

void MyThread_stop( MyThread *self )
{
  ANY_REQUIRE( self );

  MyThread_setStatus( self, MYTHREAD_TERMINATE );

  Threads_join( &(self->thread), (void**)NULL );
}

void MyThread_clear( MyThread *self )
{
  ANY_REQUIRE( self );

  ANY_FREE( self->name );
  Threads_clear( &(self->thread) );

  Mutex_clear( &self->lock );
}

void MyThread_delete( MyThread *self )
{
  ANY_REQUIRE( self );

  ANY_FREE( self );
}

void *MyThread_threadMain( void *instance )
{
  MyThread *self = (MyThread*)instance;

  ANY_REQUIRE( self );

  MyThread_setStatus( self, MYTHREAD_RUNNING );

  while ( true )
  {
    if ( MyThread_getStatus( self ) & MYTHREAD_TERMINATE )
    {
      ANY_LOG( 0, "'%s' got a termination, quitting from main loop",
               ANY_LOG_INFO, self->name );
      break;
    }

    ANY_TRACE( 5, "%s", self->name );

    Any_sleepMilliSeconds( 200 + rand() % 100 );
  }

  MyThread_setStatus( self, MYTHREAD_STOPPED );

  return( NULL );
}


int main( int argc, char *argv[] )
{
  MyThread *t1;
  MyThread *t2;
  char c = '\0';

  t1 = MyThread_new();
  MyThread_init( t1, (char*)"Prova" );

  t2 = MyThread_new();
  MyThread_init( t2, (char*)"Test" );

  MyThread_start( t1 );
  MyThread_start( t2 );

  ANY_LOG( 0, "Type 'q' and Enter to quit: ", ANY_LOG_INFO );

  while ( c != 'q' )
  {
    c = getc( stdin );
  }

  MyThread_stop( t1 );
  ANY_REQUIRE( t1->threadStatus == MYTHREAD_STOPPED );

  MyThread_stop( t2 );
  ANY_REQUIRE( t2->threadStatus == MYTHREAD_STOPPED );

  MyThread_clear( t2 );
  MyThread_delete( t2 );

  MyThread_clear( t1 );
  MyThread_delete( t1 );

  return( 0 );
}


/* EOF */
