/*
 *  Copyright (c) Honda Research Institute Europe GmbH
 *
 *  This file is part of ToolBOSLib.
 *
 *  ToolBOSLib is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  ToolBOSLib is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with ToolBOSLib. If not, see <http://www.gnu.org/licenses/>.
 */


/* some API parameters unused but kept for polymorphism */
#if defined(__GNUC__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#endif


#define BUFLEN          ( 256 )
#define MSG_COUNT       ( 100 )
#define MSG_LEN         ( 32 )
#define NUM_MSG         ( 10 )
#define BUFFSIZE   255
#define MAX_SIZE  100

#if !defined(__windows__)

#include <unistd.h>

#endif


#include <Any.h>
#include <IOChannel.h>
#include <MThreads.h>
#include <BerkeleySocketServer.h>
#include <BerkeleySocketClient.h>

#include <CuTest.h>

struct MutexAndCondition {
    Mutex *mutex;
    Cond *cond;
};

// Global "error occured" flag. Set to true when an error occured within a thread.
bool errorOccured = false;


/*---------------------------------------------------------------------------*/
/*                                 Prototypes                                */
/*---------------------------------------------------------------------------*/

// For Test #1
void *routine1_serverThread( void *arg );

void *routine1_clientThread( void *arg );

// For Test #2
void *routine2_serverThread( void *arg );

void *routine2_clientThread( void *arg );

// For Test #3
void *routine3_serverThread( void *arg );

void *routine3_clientThread( void *arg );

// For Test #4
void *routine4_serverThread( void *arg );

void *routine4_clientThread( void *arg );

// For Test #5
void *multiClient_serverThread( void *arg );

void *multiClient_clientThread_1( void *arg );

void *multiClient_clientThread_2( void *arg );

static bool multiClient_clientReadyCallBack( BerkeleySocket *self, void *data );

static bool multiClient_timeoutCallBack( BerkeleySocket *self, void *data );

// For Test #6
void *tcp_server( void *arg );

void *tcp_client( void *arg );

// For Test #7
void *udp_server( void *arg );

void *udp_client( void *arg );

// For Test #8
void *udp_broadcast_server( void *arg );

void *udp_broadcast_client( void *arg );

// For Test #9
void *blockNetworkTest_TCP_serverThread( void *arg );

void *blockNetworkTest_TCP_clientThread( void *arg );

static void blockNetworkTest_readBlock( BerkeleySocket *newBerkeleySocket );

static void blockNetworkTest_writeBlock( BerkeleySocket *myBerkeleySocket, int blockSize );

// For Test #11
void *BerkeleyData_serverThread( void *arg );

void *BerkeleyData_clientThread( void *arg );

bool BerkeleyData_readString( BerkeleySocket *newBerkeleySocket );

bool BerkeleyData_readInteger( BerkeleySocket *newBerkeleySocket );

bool BerkeleyData_readFloat( BerkeleySocket *newBerkeleySocket );

bool BerkeleyData_readDouble( BerkeleySocket *newBerkeleySocket );

bool BerkeleyData_writeString( BerkeleySocket *myBerkeleySocket );

bool BerkeleyData_writeInteger( BerkeleySocket *myBerkeleySocket, bool swapBytes );

bool BerkeleyData_writeFloat( BerkeleySocket *myBerkeleySocket, bool swapBytes );

bool BerkeleyData_writeDouble( BerkeleySocket *myBerkeleySocket, bool swapBytes );

void BerkeleyData_swapByteOrder( char *data, int len );


void Test_IOChannel_ClientServer_01( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    ANY_REQUIRE( threadServer );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    ANY_REQUIRE( threadClient );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    Threads_start( threadServer, routine1_serverThread, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, routine1_clientThread, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadClient );
    Threads_clear( threadServer );
    Threads_delete( threadClient );
    Threads_delete( threadServer );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}


void Test_IOChannel_ClientServer_02( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    ANY_REQUIRE( threadServer );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    ANY_REQUIRE( threadClient );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    Threads_start( threadServer, routine2_serverThread, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, routine2_clientThread, NULL );

    Threads_join( threadServer, NULL );
    Threads_join( threadClient, NULL );

    Threads_clear( threadServer );
    Threads_delete( threadServer );
    Threads_clear( threadClient );
    Threads_delete( threadClient );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}


void Test_IOChannel_ClientServer_03( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    ANY_REQUIRE( threadServer );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    ANY_REQUIRE( threadClient );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    Threads_start( threadServer, routine3_serverThread, &mutexAndCond );

    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, routine3_clientThread, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadServer );
    Threads_delete( threadServer );
    Threads_clear( threadClient );
    Threads_delete( threadClient );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}


void Test_IOChannel_ClientServer_04( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    ANY_REQUIRE( threadServer );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    ANY_REQUIRE( threadClient );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    Threads_start( threadServer, routine4_serverThread, &mutexAndCond );

    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, routine4_clientThread, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadServer );
    Threads_delete( threadServer );
    Threads_clear( threadClient );
    Threads_delete( threadClient );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}


void Test_IOChannel_MultiClientServer( CuTest *tc )
{
    Threads *threadServer  = (Threads *)NULL;
    Threads *threadClient1 = (Threads *)NULL;
    Threads *threadClient2 = (Threads *)NULL;

    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool bRetVal;
    int iRetVal;

    errorOccured = false;

    threadServer = Threads_new();
    ANY_REQUIRE( threadServer );
    Threads_init( threadServer, true );

    threadClient1 = Threads_new();
    ANY_REQUIRE( threadClient1 );
    Threads_init( threadClient1, true );

    threadClient2 = Threads_new();
    ANY_REQUIRE( threadClient2 );
    Threads_init( threadClient2, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    bRetVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( bRetVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    bRetVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( bRetVal );

    iRetVal = Mutex_lock( mutex );
    ANY_REQUIRE( iRetVal == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    Threads_start( threadServer, multiClient_serverThread, &mutexAndCond );

    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient1, multiClient_clientThread_1, NULL );
    Threads_start( threadClient2, multiClient_clientThread_2, NULL );

    iRetVal = Threads_join( threadServer, NULL );
    ANY_REQUIRE( iRetVal == 0 );
    iRetVal = Threads_join( threadClient1, NULL );
    ANY_REQUIRE( iRetVal == 0 );
    iRetVal = Threads_join( threadClient2, NULL );
    ANY_REQUIRE( iRetVal == 0 );

    Threads_clear( threadServer );
    Threads_delete( threadServer );
    Threads_clear( threadClient1 );
    Threads_delete( threadClient1 );
    Threads_clear( threadClient2 );
    Threads_delete( threadClient2 );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* Basic Test TCP Client & Server                                            */
/*---------------------------------------------------------------------------*/
void Test_TCP_ClientServer( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    CuAssertTrue( tc, threadServer != (Threads *)NULL );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    CuAssertTrue( tc, threadClient != (Threads *)NULL );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    /* Note: Client has a delay time ( Cond_wait() )in order to */
    /* be sure that the server is up before it attempts to connect.. */
    Threads_start( threadServer, tcp_server, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, tcp_client, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadClient );
    Threads_clear( threadServer );
    Threads_delete( threadClient );
    Threads_delete( threadServer );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* Basic Test UDP Client & Server                                            */
/*---------------------------------------------------------------------------*/
void Test_UDP_ClientServer( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    CuAssertTrue( tc, threadServer != (Threads *)NULL );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    CuAssertTrue( tc, threadClient != (Threads *)NULL );
    Threads_init( threadClient, true );


    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    /* Note: Client has a delay time ( Cond_wait() )in order to */
    /* be sure that the server is up before it attempts to connect.. */
    Threads_start( threadServer, udp_server, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, udp_client, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadClient );
    Threads_clear( threadServer );
    Threads_delete( threadClient );
    Threads_delete( threadServer );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* Broadcast Test UDP Client & Server                                        */
/*---------------------------------------------------------------------------*/
void Test_UDP_Broadcast( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    CuAssertTrue( tc, threadServer != (Threads *)NULL );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    CuAssertTrue( tc, threadClient != (Threads *)NULL );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    /* Note: Client has a delay time ( Cond_wait() )in order to */
    /* be sure that the server is up before it attempts to connect.. */
    Threads_start( threadServer, udp_broadcast_server, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, udp_broadcast_client, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadClient );
    Threads_clear( threadServer );
    Threads_delete( threadClient );
    Threads_delete( threadServer );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* Block Network test Client & Server   (including BerkeleySocket tests)     */
/*---------------------------------------------------------------------------*/
void Test_TCP_Block( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    CuAssertTrue( tc, threadServer != (Threads *)NULL );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    CuAssertTrue( tc, threadClient != (Threads *)NULL );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    /* Note: Client has a delay time ( Cond_wait() )in order to */
    /* be sure that the server is up before it attempts to connect.. */
    Threads_start( threadServer, blockNetworkTest_TCP_serverThread, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, blockNetworkTest_TCP_clientThread, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadClient );
    Threads_clear( threadServer );
    Threads_delete( threadClient );
    Threads_delete( threadServer );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* BerkeleySocket timeout tests                                              */
/*---------------------------------------------------------------------------*/
void Test_Berkeley_Timeouts( CuTest *tc )
{
    BerkeleySocket *myBerkeleySocket = (BerkeleySocket *)NULL;
    long int       tmout             = 0;

    errorOccured = false;

    myBerkeleySocket = BerkeleySocket_new();
    if( myBerkeleySocket == (BerkeleySocket *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( BerkeleySocket_init( myBerkeleySocket ) == false )
        {
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "Test #10 - Set all timeouts (but the Linger timeout ) to 10 seconds", ANY_LOG_INFO );
            BerkeleySocket_setDefaultTimeout( myBerkeleySocket, BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) );

            /* timeouts are stored as micro-seconds (1/10^6 sec) */
            tmout = BerkeleySocket_getConnectTimeout( myBerkeleySocket ) / 1000000;
            ANY_LOG( 5, "Test #10 - Check for Connect timeout. Should be 10 seconds and is [%ld]", ANY_LOG_INFO,
                     tmout );
            if( tmout != 10 )
            {
                errorOccured = true;
            }

            tmout = BerkeleySocket_getIsReadPossibleTimeout( myBerkeleySocket ) / 1000000;
            ANY_LOG( 5, "Test #10 - Check for IsReadPossible timeout. Should be 10 seconds and is [%ld]", ANY_LOG_INFO,
                     tmout );
            if( tmout != 10 )
            {
                errorOccured = true;
            }

            tmout = BerkeleySocket_getIsWritePossibleTimeout( myBerkeleySocket ) / 1000000;
            ANY_LOG( 5, "Test #10 - Check for IsWritePossible timeout. Should be 10 seconds and is [%ld]", ANY_LOG_INFO,
                     tmout );
            if( tmout != 10 )
            {
                errorOccured = true;
            }

            ANY_LOG( 5, "Test #10 - Set the Linger timeout to 10 seconds", ANY_LOG_INFO );
            BerkeleySocket_setLinger( myBerkeleySocket, true, BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) );

            tmout = BerkeleySocket_getLingerTimeout( myBerkeleySocket ) / 1000000;
            ANY_LOG( 5, "Test #10 - Check for Linger timeout. Should be 10 seconds and is [%ld]", ANY_LOG_INFO, tmout );
            if( tmout != 10 )
            {
                errorOccured = true;
            }
            BerkeleySocket_clear( myBerkeleySocket );
        }
        BerkeleySocket_delete( myBerkeleySocket );
    }

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* BerkeleySocket data tests                                                 */
/*---------------------------------------------------------------------------*/
void Test_Berkeley_Data( CuTest *tc )
{
    Threads *threadServer = (Threads *)NULL;
    Threads *threadClient = (Threads *)NULL;
    Cond *serverStartedCond;
    Mutex *mutex;
    MutexAndCondition mutexAndCond;
    bool retVal;
    int status;

    errorOccured = false;

    threadServer = Threads_new();
    CuAssertTrue( tc, threadServer != (Threads *)NULL );
    Threads_init( threadServer, true );

    threadClient = Threads_new();
    CuAssertTrue( tc, threadClient != (Threads *)NULL );
    Threads_init( threadClient, true );

    serverStartedCond = Cond_new();
    ANY_REQUIRE( serverStartedCond );
    retVal = Cond_init( serverStartedCond, COND_PRIVATE );
    ANY_REQUIRE( retVal );

    mutex = Mutex_new();
    ANY_REQUIRE( mutex );
    retVal = Mutex_init( mutex, MUTEX_PRIVATE );
    ANY_REQUIRE( retVal );

    status = Mutex_lock( mutex );
    ANY_REQUIRE( status == 0 );

    Cond_setMutex( serverStartedCond, mutex );

    mutexAndCond.mutex = mutex;
    mutexAndCond.cond = serverStartedCond;

    /* Note: Client has a delay time ( Cond_wait() )in order to */
    /* be sure that the server is up before it attempts to connect.. */
    Threads_start( threadServer, BerkeleyData_serverThread, &mutexAndCond );

    // Wait for server thread to start
    Cond_wait( serverStartedCond, 0 );

    Threads_start( threadClient, BerkeleyData_clientThread, NULL );

    Threads_join( threadClient, NULL );
    Threads_join( threadServer, NULL );

    Threads_clear( threadClient );
    Threads_clear( threadServer );
    Threads_delete( threadClient );
    Threads_delete( threadServer );

    Mutex_clear( mutex );
    Mutex_delete( mutex );
    Cond_clear( serverStartedCond );
    Cond_delete( serverStartedCond );

    CuAssertTrue( tc, !errorOccured );
}

/*---------------------------------------------------------------------------*/
/* IOChannel open Tcp test                                                   */
/*---------------------------------------------------------------------------*/
void Test_IOChannel_openTcp( CuTest *tc )
{
    unsigned int i        = 0;
    IOChannel    *channel = (IOChannel *)NULL;
    bool         status   = false;

    errorOccured = false;

    ANY_LOG( 5, "Test #12 : Create new IOChannel", ANY_LOG_INFO );
    channel = IOChannel_new();
    if( channel == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        ANY_LOG( 5, "Test #12 : Init new IOChannel", ANY_LOG_INFO );
        if( !IOChannel_init( channel ) )
        {
            errorOccured = true;
        }
        else
        {
            /* try to connect to a service which (hopefully ;-) does not exist */
            ANY_LOG( 5, "Test #12 : Try 5 times to connect to Tcp://127.0.0.1:12223...", ANY_LOG_INFO );
            for( i = 0; i < 5; i++ )
            {
                ANY_LOG( 5, "Test #12 : Try #%d ", ANY_LOG_INFO, i );

                // Connection is supposed to fail
                status = IOChannel_open( channel, "Tcp://127.0.0.1:12223", IOCHANNEL_MODE_RW,
                                         IOCHANNEL_PERMISSIONS_ALL );
                CuAssertTrue( tc, !status );
                if( status )
                {
                    ANY_LOG( 5, "Test #12 : Abnormal success while trying to connect to Tcp://127.0.0.1:12223",
                             ANY_LOG_WARNING );
                }
            }
            ANY_LOG( 5, "Test #12 : Clear IOChannel", ANY_LOG_INFO );
            IOChannel_clear( channel );
        }
        ANY_LOG( 5, "Test #12 : Delete IOChannel", ANY_LOG_INFO );
        IOChannel_delete( channel );
    }
    CuAssertTrue( tc, !errorOccured );
}


/*---------------------------------------------------------------------------*/
/* IOChannel printf test                                                     */
/*---------------------------------------------------------------------------*/
void Test_IOChannel_printf( CuTest *tc )
{
    IOChannel *channel = (IOChannel *)NULL;
    bool      status   = false;

    errorOccured = false;

    channel = IOChannel_new();
    if( channel == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !IOChannel_init( channel ) )
        {
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "Test #13 : Try to open IOChannel on StdOut", ANY_LOG_INFO );
            status = IOChannel_open( channel, "StdOut://", IOCHANNEL_MODE_W_ONLY, IOCHANNEL_PERMISSIONS_ALL );
            CuAssertTrue( tc, status );
            if( !status )
            {
                errorOccured = true;
                ANY_LOG( 5, "Test #13 : Cannot open IOChannel on StdOut", ANY_LOG_INFO );
            }
            else
            {
                ANY_LOG( 5, "Test #13 : Use IOChannel_printf on StdOut", ANY_LOG_INFO );
                IOChannel_printf( channel,
                                  "Test #13 : This is an escaped string '%S' displayed using IOChannel_printf.\n",
                                  "\n\f\0xde" );
            }
            ANY_LOG( 5, "Test #13 : Clear the IOChannel", ANY_LOG_INFO );
            IOChannel_clear( channel );
        }
        ANY_LOG( 5, "Test #13 : Delete the IOChannel", ANY_LOG_INFO );
        IOChannel_delete( channel );
    }
}


void Test_NameResolv( CuTest *tc )
{
    IOChannel    *stream                          = (IOChannel *)NULL;
    char         hostname[]                       = "localhost";
    unsigned int port                             = 1234;
    char         url[IOCHANNEL_INFOSTRING_MAXLEN] = "";
    int          status                           = 0;

    stream = IOChannel_new();
    IOChannel_init( stream );

    Any_sprintf( url, "stream=Udp host=%s port=%d mode=IOCHANNEL_MODE_W_ONLY", hostname, port );

    status = IOChannel_openFromString( stream, url );

    if( ! status )
    {
        ANY_LOG( 0, "Can not open IOChannel '%s'", ANY_LOG_ERROR, url );
    }

    CuAssertPtrNotNull( tc, stream );
    CuAssertTrue( tc, status );

    IOChannel_clear( stream );
    IOChannel_delete( stream );
}


/*---------------------------------------------------------------------------*/
/* Helpers                                                                   */
/*---------------------------------------------------------------------------*/

// For Test_IOChannel_ClientServer_01
void *routine1_serverThread( void *arg )
{
    int status;
    char               Sc          = '\0';
    unsigned int       Su          = 0;
    int                Si          = 0;
    float              Sf          = 0;
    long double        SLf         = 0;
    char               Sstring[20] = "";
    unsigned short int Shu         = 0;
    short int          Shd         = 0;
    unsigned long int  Slu         = 0;
    long int           Sld         = 0;
    void               *address    = 0;
    const char         *format     = "%c %u\n %d %fpatternTo 1024\n10-24 Match%Lf %s %hu %hd %lu %ld %p\n";
    IOChannel          *stream     = (IOChannel *)NULL;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );

    /* New and Init IOChannel */
    stream = IOChannel_new();
    if( stream == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !IOChannel_init( stream ) )
        {
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "SERVER: Test #1 - Opening a ServerTcp:// Stream on port[60002]!", ANY_LOG_INFO );

            /* ServerTcp:// is a blocking stream: IOChannel_open do not returns   */
            /* until a client connects or the timeout is over */

            /* Let the test case start the client thread */
            Cond_signal( mutexAndCond->cond );

            status = Mutex_unlock( mutexAndCond->mutex );
            ANY_REQUIRE( status == 0 );

            if( IOChannel_openFromString( stream, "stream=ServerTcp port=60002 reuseAddr=1" ) == false )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "SERVER: Test #1 - Before read:  %c %u %d %f %Lf %s %hu %hd %lu %ld %p", ANY_LOG_INFO, Sc,
                         Su, Si, Sf, SLf, Sstring, Shu, Shd, Slu, Sld, address );

                IOChannel_scanf( stream, NULL, (char *)format, &Sc, &Su, &Si, &Sf, &SLf, Sstring, &Shu, &Shd, &Slu,
                                 &Sld, &address );

                ANY_LOG( 5, "SERVER: Test #1 - After read:  %c %u %d %f %Lf %s %hu %hd %lu %ld %p", ANY_LOG_INFO, Sc,
                         Su, Si, Sf, SLf, Sstring, Shu, Shd, Slu, Sld, address );

                ANY_LOG( 5, "SERVER: Test #1 - Read Bytes[%ld]. Closing Connection...", ANY_LOG_INFO,
                         IOChannel_getReadBytes( stream ) );

                // Check that what we read is what we sent (values are taken from the routine1_clientThread() )
                if( Sc != 99 )
                {
                    errorOccured = true;
                }
                if( Su != 1 )
                {
                    errorOccured = true;
                }
                if( Si != 2 )
                {
                    errorOccured = true;
                }
                if( Sf != 3.5 )
                {
                    errorOccured = true;
                }
                if( strcmp( Sstring, "string" ) != 0 )
                {
                    errorOccured = true;
                }
                if( SLf != 4.5 )
                {
                    errorOccured = true;
                }
                if( Shu != 5 )
                {
                    errorOccured = true;
                }
                if( Shd != 6 )
                {
                    errorOccured = true;
                }
                if( Slu != 7 )
                {
                    errorOccured = true;
                }
                if( Sld != 8 )
                {
                    errorOccured = true;
                }

                IOChannel_close( stream );
            }
            IOChannel_clear( stream );
        }
        IOChannel_delete( stream );
    }

    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_01
void *routine1_clientThread( void *arg )
{
    char               c         = 'c';
    unsigned int       u         = 1;
    int                i         = 2;
    float              f         = 3.5;
    const char         *string   = "string";
    long double        Lf        = 4.5;
    unsigned short int hu        = 5;
    short int          hd        = 6;
    unsigned long int  lu        = 7;
    long int           ld        = 8;
    Cond               *condWait = (Cond *)NULL;
    IOChannel          *stream   = (IOChannel *)NULL;


    /* Wait to be sure that the server up */
    condWait = Cond_new();
    if( condWait == (Cond *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        /* New and  Init IOChannel */
        stream = IOChannel_new();
        if( stream == (IOChannel *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !IOChannel_init( stream ) )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #1 - Connecting on port[60002]..", ANY_LOG_INFO );

                if( IOChannel_open( stream, "Tcp://127.0.0.1:60002",
                                    IOCHANNEL_MODE_RW | IOCHANNEL_MODE_CREAT | IOCHANNEL_MODE_TRUNC,
                                    IOCHANNEL_PERMISSIONS_ALL ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    /* Let Create A Large Buffer to Allow AutoCalcsize */
                    IOChannel_setWriteBuffer( stream, (void *)NULL, 1024 );
                    IOChannel_setUseWriteBuffering( stream, true, true );

                    /* Write data */
                    ANY_LOG( 5, "CLIENT: Test #1 - Sending Data....", ANY_LOG_INFO );

                    IOChannel_printf( stream, "  %c %u\n %d %fpatternTo \n1024\n10-24 Match%Lf %s %hu %hd %lu %ld %p\n",
                                      &c, &u, &i, &f, &Lf, string, &hu, &hd, &lu, &ld, (void *)&Lf );

                    ANY_LOG( 5, "CLIENT: Test #1 - Written Bytes[%ld]. Closing Connection", ANY_LOG_INFO,
                             IOChannel_getWrittenBytes( stream ) );

                    IOChannel_close( stream );
                }
                IOChannel_clear( stream );
            }
            IOChannel_delete( stream );
        }

        Cond_clear( condWait );
        Cond_delete( condWait );
    }


    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_02
void *routine2_serverThread( void *arg )
{
    BerkeleySocketServer *socketServer   = (BerkeleySocketServer *)NULL;
    BerkeleySocket       *sockPtr        = (BerkeleySocket *)NULL;
    BerkeleySocket       *newClient      = (BerkeleySocket *)NULL;
    IOChannel            *stream         = (IOChannel *)NULL;
    bool                 status          = false;
    int                  port            = 0;
    int                  maxNumOfClients = 1;
    int                  istatus;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    istatus = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( istatus == 0 );


    socketServer = BerkeleySocketServer_new();
    if( socketServer == (BerkeleySocketServer *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        status = BerkeleySocketServer_init( socketServer, NULL );
        if( !status )
        {
            errorOccured = true;
        }
        else
        {
            port    = 43999;
            BerkeleySocket *socket = BerkeleySocketServer_getSocket( socketServer );
            BerkeleySocket_setReuseAddr( socket, true );

            sockPtr = BerkeleySocketServer_connect( socketServer, BERKELEYSOCKET_TCP, port, maxNumOfClients );
            if( sockPtr == (BerkeleySocket *)NULL )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "SERVER: Test #2 - listen on port[%d]", ANY_LOG_INFO, port );

                /* Let the test case start the client thread */
                Cond_signal( mutexAndCond->cond );

                istatus = Mutex_unlock( mutexAndCond->mutex );
                ANY_REQUIRE( istatus == 0 );

                /* Wait incoming Clients */
                if( !BerkeleySocketServer_waitClient( socketServer, BERKELEYSOCKET_TIMEOUT_SECONDS( 600 ) ) )
                {
                    errorOccured = true;
                }
                else
                {
                    /* init iostream */
                    IOChannelMode        modes       =
                                                 IOCHANNEL_MODE_CREAT | IOCHANNEL_MODE_RW | IOCHANNEL_MODE_NOTCLOSE;
                    IOChannelPermissions permissions = IOCHANNEL_PERMISSIONS_ALL;

                    ANY_LOG( 5, "SERVER: Test #2 - A client is connecting..", ANY_LOG_INFO );

                    stream = IOChannel_new();
                    if( stream == (IOChannel *)NULL )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        if( !IOChannel_init( stream ) )
                        {
                            errorOccured = true;
                        }
                        else
                        {
                            /* Foreach you are going to serve, you need a new socket  */
                            newClient = BerkeleySocket_new();
                            if( newClient == (BerkeleySocket *)NULL )
                            {
                                errorOccured = true;
                            }
                            else
                            {
                                if( BerkeleySocket_init( newClient ) == false )
                                {
                                    errorOccured = true;
                                }
                                else
                                {
                                    /* Accept the Client and assing it the sockForClient socket */
                                    BerkeleySocketServer_acceptClient( socketServer, newClient );
                                    if( IOChannel_open( stream, "Socket://", modes, permissions, newClient ) == false )
                                    {
                                        errorOccured = true;
                                    }
                                    else
                                    {
                                        /* Write Read Data */
                                        if( IOChannel_isWritePossible( stream ) == true )
                                        {
                                            ANY_LOG( 5, "SERVER: Test #2 - Sending Data LaLaLa\n", ANY_LOG_INFO );
                                            IOChannel_printf( stream, "LaLaLa\n" );
                                            IOChannel_flush( stream );
                                        }
                                        else
                                        {
                                            ANY_LOG( 5,
                                                     "SERVER: Test #2 - IOChannel_isWritePossible() returned false!!",
                                                     ANY_LOG_INFO );
                                            errorOccured = true;
                                        }
                                        Any_sleepSeconds( 2 );
                                        ANY_LOG( 5, "SERVER: Test #2 - Closing the Stream..", ANY_LOG_INFO );
                                        IOChannel_close( stream );
                                    }
                                    /* The NOTCLOSE flag was specified, so must disconnect it... */
                                    BerkeleySocket_disconnect( newClient );
                                    BerkeleySocket_clear( newClient );
                                }
                                BerkeleySocket_delete( newClient );
                            }
                            IOChannel_clear( stream );
                        }
                        IOChannel_delete( stream );
                    }
                }
                BerkeleySocketServer_disconnect( socketServer );
            }
            BerkeleySocketServer_clear( socketServer );
            BerkeleySocketServer_delete( socketServer );
        }
    }
    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_02
void *routine2_clientThread( void *arg )
{
    int port = 43999;

    BerkeleySocketClient *socketClient = (BerkeleySocketClient *)NULL;
    BerkeleySocket       *sockPtr      = (BerkeleySocket *)NULL;
    IOChannel            *stream       = (IOChannel *)NULL;
    Cond                 *condWait     = (Cond *)NULL;
    IOChannelMode        modes         = IOCHANNEL_MODE_R_ONLY | IOCHANNEL_MODE_NOTCLOSE;
    IOChannelPermissions permissions   = IOCHANNEL_PERMISSIONS_ALL;
    const char           *srvAddrs     = "127.0.0.1";


    /* Wait to be sure that the server up */
    condWait   = Cond_new();
    if( condWait == (Cond *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        socketClient = BerkeleySocketClient_new();
        if( socketClient == (BerkeleySocketClient *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( BerkeleySocketClient_init( socketClient, NULL ) == false )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #2 - Connecting to the server..port[%d]", ANY_LOG_INFO, port );

                sockPtr = BerkeleySocketClient_connect( socketClient, BERKELEYSOCKET_TCP, (char *)srvAddrs, port );
                if( sockPtr == (BerkeleySocket *)NULL )
                {
                    errorOccured = true;
                }
                else
                {
                    stream = IOChannel_new();
                    if( stream == (IOChannel *)NULL )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        if( !IOChannel_init( stream ) )
                        {
                            errorOccured = true;
                        }
                        else
                        {
                            if( IOChannel_open( stream, "Socket://", modes, permissions, sockPtr ) == false )
                            {
                                errorOccured = true;
                                ANY_LOG( 5, "CLIENT: Test #2 - Errorcode %s \n\n", ANY_LOG_INFO,
                                         IOChannel_getErrorDescription( stream ) );
                            }
                            else
                            {
                                char buffer[16];
                                memset( buffer, '\0', sizeof( buffer ) );
                                ANY_LOG( 5, "CLIENT: Test #2 - Reading from the server..", ANY_LOG_INFO );

                                if( IOChannel_isReadDataAvailable( stream ) == true )
                                {
                                    IOChannel_gets( stream, buffer, sizeof( buffer ) );
                                    ANY_LOG( 5, "CLIENT: Test #2 - Received Data [%s]\n", ANY_LOG_INFO, buffer );
                                    if( strcmp( buffer, "LaLaLa" ) != 0 )
                                    {
                                        errorOccured = true;
                                    }
                                }
                                else
                                {
                                    errorOccured = true;
                                    ANY_LOG( 5, "CLIENT: Test #2 - IOChannel_isReadDataAvailable() returned false",
                                             ANY_LOG_INFO );
                                }
                                ANY_LOG( 5, "CLIENT: Test #2 - Closing the Stream..", ANY_LOG_INFO );
                                IOChannel_close( stream );
                            }
                            IOChannel_clear( stream );
                        }
                        IOChannel_delete( stream );
                    }
                    BerkeleySocketClient_disconnect( socketClient );
                }
                BerkeleySocketClient_clear( socketClient );
            }
            BerkeleySocketClient_delete( socketClient );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }
    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_03
void *routine3_serverThread( void *arg )
{
    IOChannel  *stream  = (IOChannel *)NULL;
    char       string[50];
    int        number   = 0;
    long int   bytes    = 0;
    long int   lnumber  = 0;
    const char *fString = "%s";
    const char *fInt    = "%d";
    int status;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );


    memset( string, '\0', sizeof( string ) );

    stream     = IOChannel_new();
    if( stream == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !IOChannel_init( stream ) )
        {
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "SERVER: Test #3 - Opening a ServerTcp:// Stream on port[60002]!", ANY_LOG_INFO );

            /* Let the test case start the client thread */
            Cond_signal( mutexAndCond->cond );

            status = Mutex_unlock( mutexAndCond->mutex );
            ANY_REQUIRE( status == 0 );

            /* This is a blocking stream: IOChannel_open do not returns until  */
            /* a client connects or the timeout is over */
            if( IOChannel_openFromString( stream, "stream=ServerTcp port=60002 reuseAddr=1" ) == false )
            {
                errorOccured = true;
            }
            else
            {
                /* Reading string Data */
                lnumber = IOChannel_getIsReadDataAvailableTimeout( stream );
                ANY_LOG( 5, "SERVER: Test #3 - Current timeout for read is( usecs ): [%ld]", ANY_LOG_INFO, lnumber );

                ANY_LOG( 5, "SERVER: Test #3 - Changing timeout for read to 1500 usecs", ANY_LOG_INFO );
                IOChannel_setIsReadDataAvailableTimeout( stream, 1500 );

                if( IOChannel_isReadDataAvailable( stream ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    IOChannel_scanf( stream, NULL, (char *)fString, string );
                    if( IOChannel_isErrorOccurred( stream ) == true )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        ANY_LOG( 5, "SERVER: Test #3 - Read Data..[%s]", ANY_LOG_INFO, string );
                    }

                    IOChannel_scanf( stream, NULL, (char *)fInt, &number );
                    if( IOChannel_isErrorOccurred( stream ) == true )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        ANY_LOG( 5, "SERVER: Test #3 - Read Data..[%d]", ANY_LOG_INFO, number );
                    }

                    bytes = IOChannel_getReadBytes( stream );
                    ANY_LOG( 5, "SERVER: Test #3 - Downloaded (read)bytes: [%ld]. Closing the connection..",
                             ANY_LOG_INFO, bytes );
                    if( bytes != 15 )
                    {
                        errorOccured = true;
                    }
                }
                IOChannel_close( stream );
            }
            IOChannel_clear( stream );
        }
        IOChannel_delete( stream );
    }
    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_03
void *routine3_clientThread( void *arg )
{
    IOChannel            *stream      = (IOChannel *)NULL;
    IOChannelMode        mode         = IOCHANNEL_MODE_RW | IOCHANNEL_MODE_CREAT | IOCHANNEL_MODE_TRUNC;
    IOChannelPermissions permissions  = IOCHANNEL_PERMISSIONS_ALL;
    Cond                 *condWait    = (Cond *)NULL;
    long int             longNum      = 0;
    int                  numberToSend = 2;

    const char *stringToSend = "stringToSend";
    const char *streamType   = "Tcp://127.0.0.1:60002";


    /* Wait to be sure that the server up */
    condWait   = Cond_new();
    if( condWait == (Cond *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        stream = IOChannel_new();
        if( stream == (IOChannel *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !IOChannel_init( stream ) )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #3 - Connecting to Tcp://127.0.0.1:60002", ANY_LOG_INFO );
                if( IOChannel_open( stream, streamType, mode, permissions ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    longNum = IOChannel_getIsWritePossibleTimeout( stream );
                    ANY_LOG( 5, "CLIENT: Test #3 - Current timeout for write is( usecs ): [%ld]", ANY_LOG_INFO,
                             longNum );

                    IOChannel_setIsWritePossibleTimeout( stream, 2000 );

                    longNum = IOChannel_getIsWritePossibleTimeout( stream );
                    ANY_LOG( 5, "CLIENT: Test #3 - Changing timeout for write to( usecs ): [%ld]", ANY_LOG_INFO,
                             longNum );
                    if( longNum != 2000 )
                    {
                        errorOccured = true;
                    }

                    /* Remember to use the trailing separator! You can use simply the space... */
                    ANY_LOG( 5, "CLIENT: Test #3 - Sending Data..[%s][%d]", ANY_LOG_INFO, stringToSend, numberToSend );

                    if( IOChannel_isWritePossible( stream ) == true )
                    {
                        IOChannel_printf( stream, "%s ", stringToSend );
                        IOChannel_printf( stream, "%d ", &numberToSend );
                    }

                    longNum = IOChannel_getWrittenBytes( stream );
                    ANY_LOG( 5, "CLIENT: Test #3 - The Number of Written Bytes is : %ld. Closing connection",
                             ANY_LOG_INFO, longNum );
                    IOChannel_close( stream );
                }
                IOChannel_clear( stream );
            }
            IOChannel_delete( stream );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }
    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_04
void *routine4_serverThread( void *arg )
{
    long int     var     = 0;
    unsigned int i       = 0;
    IOChannel    *stream = (IOChannel *)NULL;
    const char   *format = "%ld";
    int status;

    MutexAndCondition *mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );


    /* New and  Init IOChannel */
    stream     = IOChannel_new();
    if( stream == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !IOChannel_init( stream ) )
        {
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "SERVER: Test #4 - Opening a ServerTcp:// Stream on port[60002]!", ANY_LOG_INFO );

            /* Let the test case start the client thread */
            Cond_signal( mutexAndCond->cond );

            status = Mutex_unlock( mutexAndCond->mutex );
            ANY_REQUIRE( status == 0 );

            /* ServerTcp:// is a blocking stream: IOChannel_open do not returns   */
            /* until a client connects or the timeout is over */
            if( IOChannel_openFromString( stream, "stream=ServerTcp port=60002 reuseAddr=1" ) == false )
            {
                errorOccured = true;
            }
            else
            {
                if( IOChannel_isReadDataAvailable( stream ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    while( ( i < 5 ) && ( IOChannel_isErrorOccurred( stream ) == false ) )
                    {
                        /* Read Data */
                        IOChannel_scanf( stream, NULL, (char *)format, &var );
                        if( IOChannel_isErrorOccurred( stream ) == false )
                        {
                            ANY_LOG( 5, "SERVER: Test #4 - Read long int [%ld]", ANY_LOG_INFO, var );
                            switch( i )
                            {
                                case 0:
                                    if( var != 1804289383 )
                                    {
                                        errorOccured = true;
                                    }
                                    break;
                                case 1:
                                    if( var != 846930886 )
                                    {
                                        errorOccured = true;
                                    }
                                    break;
                                case 2:
                                    if( var != 1681692777 )
                                    {
                                        errorOccured = true;
                                    }
                                    break;
                                case 3:
                                    if( var != 1714636915 )
                                    {
                                        errorOccured = true;
                                    }
                                    break;
                                case 4:
                                    if( var != 1957747793 )
                                    {
                                        errorOccured = true;
                                    }
                                    break;
                            }
                            i++;
                        }
                    }
                    if( IOChannel_isErrorOccurred( stream ) == true )
                    {
                        ANY_LOG( 5, "SERVER: Test #4 - IOChannel reported the following error: %s", ANY_LOG_WARNING,
                                 IOChannel_getErrorDescription( stream ) );
                        errorOccured = true;
                    }
                    else
                    {
                        var = IOChannel_getReadBytes( stream );
                        ANY_LOG( 5, "SERVER: Test #4 - Read Bytes[%ld].", ANY_LOG_INFO, var );
                        ANY_LOG( 5, "SERVER: Test #4 - End of stream...", ANY_LOG_INFO );
                    }
                }
                ANY_LOG( 5, "SERVER: Test #4 - Closing Connection...", ANY_LOG_INFO );
                IOChannel_close( stream );
            }
            IOChannel_clear( stream );
        }
        IOChannel_delete( stream );
    }
    return (void *)NULL;
}


// For Test_IOChannel_ClientServer_04
void *routine4_clientThread( void *arg )
{
    Cond         *condWait = (Cond *)NULL;
    IOChannel    *stream   = (IOChannel *)NULL;
    long int     var       = 0;
    unsigned int i         = 0;


    /* Wait to be sure that the server up */
    condWait   = Cond_new();
    if( condWait == (Cond *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        stream = IOChannel_new();
        if( stream == (IOChannel *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !IOChannel_init( stream ) )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #4 - Connecting on port[60002]..", ANY_LOG_INFO );

                if( IOChannel_open( stream, "Tcp://127.0.0.1:60002",
                                    IOCHANNEL_MODE_RW | IOCHANNEL_MODE_CREAT | IOCHANNEL_MODE_TRUNC,
                                    IOCHANNEL_PERMISSIONS_ALL ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    /* Let Create A Large Buffer to Allow AutoCalcsize */
                    IOChannel_setWriteBuffer( stream, (void *)NULL, 1024 );
                    IOChannel_setUseWriteBuffering( stream, true, true );

                    ANY_LOG( 5, "CLIENT: Test #4 - Sending Random Data:", ANY_LOG_INFO );
                    for( ; i < 5; i++ )
                    {
                        switch( i )
                        {
                            case 0:
                                var = 1804289383;
                                break;
                            case 1:
                                var = 846930886;
                                break;
                            case 2:
                                var = 1681692777;
                                break;
                            case 3:
                                var = 1714636915;
                                break;
                            case 4:
                                var = 1957747793;
                                break;
                        }
                        /* Write data */
                        ANY_LOG( 5, "CLIENT: Test #4 - Sending [%ld]....", ANY_LOG_INFO, var );
                        IOChannel_printf( stream, "%ld ", &var );
                        if( IOChannel_isErrorOccurred( stream ) == true )
                        {
                            errorOccured = true;
                            ANY_LOG( 5, "CLIENT: Test #4 - IOChannel reported the following error: %s", ANY_LOG_WARNING,
                                     IOChannel_getErrorDescription( stream ) );
                            break;
                        }
                    }

                    if( IOChannel_isErrorOccurred( stream ) == false )
                    {
                        var = IOChannel_getWrittenBytes( stream );
                        ANY_LOG( 5, "CLIENT: Test #4 - Written Bytes[%ld].", ANY_LOG_INFO, var );
                        ANY_LOG( 5, "CLIENT: Test #4 - Closing Connection", ANY_LOG_INFO );
                    }
                    IOChannel_close( stream );
                }
                IOChannel_clear( stream );
            }
            IOChannel_delete( stream );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }
    return (void *)NULL;
}


// For Test_IOChannel_MultiClientServer
void *multiClient_serverThread( void *arg )
{
    int                  serverPort = 60002;
    int                  maxClient  = 5;
    int                  status;
    BerkeleySocketServer *server    = (BerkeleySocketServer *)NULL;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );

    /* alloc a new BerkeleySocketServer */
    server = BerkeleySocketServer_new();
    if( server == (BerkeleySocketServer *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        /* initialize the BerkeleySocketServer */
        if( BerkeleySocketServer_init( server, NULL ) == false )
        {
            errorOccured = true;
        }
        else
        {
            BerkeleySocket *socket = BerkeleySocketServer_getSocket( server );
            BerkeleySocket_setReuseAddr( socket, true );

            /* Let the test case start the client thread */
            Cond_signal( mutexAndCond->cond );

            status = Mutex_unlock( mutexAndCond->mutex );
            ANY_REQUIRE( status == 0 );

            /* connect the BerkeleySocketServer */
            if( BerkeleySocketServer_connect( server, BERKELEYSOCKET_UDP, serverPort, maxClient ) == NULL )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "SERVER  : Test #5 - Waiting for a client ...", ANY_LOG_INFO );

                /* call the server main loop */
                BerkeleySocketServer_loop( server, multiClient_clientReadyCallBack, NULL, multiClient_timeoutCallBack,
                                           NULL, BERKELEYSOCKET_TIMEOUT_SECONDS( 1 ) );

                ANY_LOG( 5, "SERVER  : Test #5 - Disconnecting the server ...", ANY_LOG_INFO );

                BerkeleySocketServer_disconnect( server );
            }
            BerkeleySocketServer_clear( server );
        }
        BerkeleySocketServer_delete( server );
    }

    return (void *)NULL;
}


// For Test_IOChannel_MultiClientServer
void *multiClient_clientThread_1( void *arg )
{
    char                 localhost[] = "127.0.0.1";
    char                 *serverName = localhost;
    char                 hostName[128];
    char                 *serverIp   = (char *)NULL;
    int                  serverPort  = 60002;
    int                  count       = 20;
    int                  status      = 0;
    int                  data        = 0L;
    int                  r           = 0L;
    BerkeleySocketClient *client     = (BerkeleySocketClient *)NULL;
    BerkeleySocket       *sock       = (BerkeleySocket *)NULL;


    serverIp   = BerkeleySocket_host2Addr( serverName, hostName, 128 );
    if( serverIp == (char *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        /* alloc a new BerkeleySocketClient */
        client = BerkeleySocketClient_new();
        if( client == (BerkeleySocketClient *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            /* initialize the BerkeleySocketServer */
            if( !BerkeleySocketClient_init( client, NULL ) )
            {
                errorOccured = true;
            }
            else
            {
                BerkeleySocket_setDefaultTimeout( BerkeleySocketClient_getSocket( client ),
                                                  BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) );
                ANY_LOG( 5, "CLIENT 1: Test #5 - connecting to %s:%d (%s:%d)...", ANY_LOG_INFO, serverName, serverPort,
                         serverIp, serverPort );

                /* connect the BerkeleySocketClient */
                sock = BerkeleySocketClient_connect( client, BERKELEYSOCKET_UDP, serverIp, serverPort );
                if( sock == (BerkeleySocket *)NULL )
                {
                    ANY_LOG( 5, "CLIENT 1: Test #5 - Unable to connect to the server %s:%d", ANY_LOG_FATAL, serverName,
                             serverPort );
                    errorOccured = true;
                }
                else
                {
                    r = 9999999;
                    while( count-- )
                    {
                        r++;
                        ANY_LOG( 5, "CLIENT 1: Test #5 - Sending number %d ...", ANY_LOG_INFO, r );
                        data   = htonl( r );
                        status = BerkeleySocket_write( sock, (BaseUI8 *)&data, sizeof( data ) );
                        if( status != sizeof( data ) )
                        {
                            char error[128];
                            BerkeleySocket_strerror( errno, error, 128 );

                            ANY_LOG( 5, "CLIENT 1: Test #5 - Unable to send data to the server %s:%d, error '%s'",
                                     ANY_LOG_FATAL, serverName, serverPort, error );
                            errorOccured = true;
                            break;
                        }
                        Any_sleepMilliSeconds( 500 );
                    }
                    ANY_LOG( 5, "CLIENT 1: Test #5 - Disconnecting...", ANY_LOG_INFO );
                    BerkeleySocketClient_disconnect( client );
                }
                BerkeleySocketClient_clear( client );
            }
            BerkeleySocketClient_delete( client );
        }
    }
    return (void *)NULL;
}


// For Test_IOChannel_MultiClientServer
void *multiClient_clientThread_2( void *arg )
{
    char                 localhost[] = "127.0.0.1";
    char                 *serverName = localhost;
    char                 hostName[128];
    char                 *serverIp   = (char *)NULL;
    int                  serverPort  = 60002;
    int                  count       = 20;
    int                  status      = 0;
    int                  data        = 0L;
    int                  r           = 0L;
    BerkeleySocketClient *client     = (BerkeleySocketClient *)NULL;
    BerkeleySocket       *sock       = (BerkeleySocket *)NULL;


    serverIp    = BerkeleySocket_host2Addr( serverName, hostName, 128 );
    if( serverIp == (char *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        /* alloc a new BerkeleySocketClient */
        client = BerkeleySocketClient_new();
        if( client == (BerkeleySocketClient *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            /* initialize the BerkeleySocketServer */
            if( !BerkeleySocketClient_init( client, NULL ) )
            {
                errorOccured = true;
            }
            else
            {
                BerkeleySocket_setDefaultTimeout( BerkeleySocketClient_getSocket( client ),
                                                  BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) );
                ANY_LOG( 5, "CLIENT 2: Test #5 - connecting to %s:%d (%s:%d)...", ANY_LOG_INFO, serverName, serverPort,
                         serverIp, serverPort );

                /* connect the BerkeleySocketClient */
                sock = BerkeleySocketClient_connect( client, BERKELEYSOCKET_UDP, serverIp, serverPort );
                if( sock == (BerkeleySocket *)NULL )
                {
                    ANY_LOG( 5, "CLIENT 2: Test #5 - Unable to connect to the server %s:%d", ANY_LOG_FATAL, serverName,
                             serverPort );
                    errorOccured = true;
                }
                else
                {
                    r = 19999999;
                    while( count-- )
                    {
                        r++;
                        ANY_LOG( 5, "CLIENT 2: Test #5 - Sending number %d ...", ANY_LOG_INFO, r );
                        data   = htonl( r );
                        status = BerkeleySocket_write( sock, (BaseUI8 *)&data, sizeof( data ) );
                        if( status != sizeof( data ) )
                        {
                            char error[128];
                            BerkeleySocket_strerror( errno, error, 128 );

                            ANY_LOG( 5, "CLIENT 2: Test #5 - Unable to send data to the server %s:%d, error '%s'",
                                     ANY_LOG_FATAL, serverName, serverPort, error );
                            errorOccured = true;
                            break;
                        }
                        Any_sleepMilliSeconds( 300 );
                    }
                    ANY_LOG( 5, "CLIENT 2: Test #5 - Disconnecting...", ANY_LOG_INFO );
                    BerkeleySocketClient_disconnect( client );
                }
                BerkeleySocketClient_clear( client );
            }
            BerkeleySocketClient_delete( client );
        }
    }
    return (void *)NULL;
}


// For Test_IOChannel_MultiClientServer
static bool multiClient_clientReadyCallBack( BerkeleySocket *self, void *data )
{
    static int count      = 100;
    char       remoteIp[128];
    int        remotePort = 0;
    int        status     = 0;
    int        data1      = 0L;
    int        data2      = 0L;

    status = BerkeleySocket_read( self, (BaseUI8 *)&data1, sizeof( data1 ) );

    if( status == sizeof( data1 ) )
    {
        BerkeleySocket_getRemoteAddr( self, remoteIp, 128, &remotePort );
        data2 = (int)ntohl( data1 );
        ANY_LOG( 5, "SERVER  : Test #5 - New data from %s:%d is: %d", ANY_LOG_INFO, remoteIp, remotePort, data2 );
        // We roughly test what we get from the clients
        if( ( data2 < 10000000 ) || ( data2 > 20000019 ) )
        {
            errorOccured = true;
        }
    }
    else
    {
        ANY_LOG( 5, "SERVER  : Test #5 - Error reading data", ANY_LOG_WARNING );
        errorOccured = true;
    }

    /* we exit from the server loop only when timeout reach 0 */
    return ( ( --count ? false : true ) );
}


// For Test_IOChannel_MultiClientServer
static bool multiClient_timeoutCallBack( BerkeleySocket *self, void *data )
{
    static int count = 5;

    ANY_LOG( 5, "SERVER  : Test #5 - No data is available ( %d / 5 )", ANY_LOG_INFO, 6 - count );

    /* we exit from the server loop only when timeout reach 0 */
    return ( ( --count ? false : true ) );
}


// For Test_TCP_ClientServer
void *tcp_server( void *arg )
{
    IOChannel    *stream = (IOChannel *)NULL;
    char         buffer[BUFLEN];
    unsigned int i       = 0;
    int status;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );


    stream = IOChannel_new();
    if( stream == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !IOChannel_init( stream ) )
        {
            ANY_LOG( 5, "SERVER: Test #6 - TCP server init failed...", ANY_LOG_INFO );
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "SERVER: Test #6 - TCP server starts listening...", ANY_LOG_INFO );

            /* Let the test case start the client thread */
            Cond_signal( mutexAndCond->cond );

            status = Mutex_unlock( mutexAndCond->mutex );
            ANY_REQUIRE( status == 0 );

            if( IOChannel_openFromString( stream, "stream=ServerTcp port=2222 reuseAddr=1 mode='IOCHANNEL_MODE_RW' perm='IOCHANNEL_PERMISSIONS_ALL'" ) == false )
            {
                ANY_LOG( 5, "SERVER: Test #6 - TCP server channel opening failed...", ANY_LOG_INFO );
                errorOccured = true;
            }
            else
            {
                while( ( IOChannel_eof( stream ) == false ) && ( IOChannel_isErrorOccurred( stream ) == false ) &&
                       ( i < MSG_COUNT ) )
                {
                    IOChannel_read( stream, buffer, BUFLEN );
                    ANY_LOG( 5, "SERVER: Test #6 - TCP Received: %s", ANY_LOG_DATA, buffer );
                    i++;
                }

                if( ( i != MSG_COUNT ) || ( IOChannel_isErrorOccurred( stream ) == true ) )
                {
                    ANY_LOG( 5, "SERVER: Test #6 - TCP server did not get all messages...", ANY_LOG_INFO );
                    errorOccured = true;
                }

                ANY_LOG( 5, "SERVER: Test #6 - TCP server stops listening...", ANY_LOG_INFO );

                IOChannel_close( stream );
            }
            IOChannel_clear( stream );
        }
        IOChannel_delete( stream );
    }

    return (void *)NULL;
}


// For Test_TCP_ClientServer
void *tcp_client( void *arg )
{
    IOChannel    *stream   = (IOChannel *)NULL;
    const char   *url      = "Tcp://127.0.0.1:2222";
    char         buffer[BUFLEN];
    unsigned int i         = 0;
    Cond         *condWait = (Cond *)NULL;

    // Used to be sure that the server up
    condWait = Cond_new();
    if( !condWait )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        stream = IOChannel_new();
        if( stream == (IOChannel *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !IOChannel_init( stream ) )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #6 - TCP client connecting to %s", ANY_LOG_INFO, url );

                if( IOChannel_open( stream, url, IOCHANNEL_MODE_RW, IOCHANNEL_PERMISSIONS_ALL ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    ANY_LOG( 5, "CLIENT: Test #6 - TCP client starts talking", ANY_LOG_INFO );

                    while( ( IOChannel_eof( stream ) == false ) && ( IOChannel_isErrorOccurred( stream ) == false ) &&
                           ( i < MSG_COUNT ) )
                    {
                        Any_snprintf( buffer, BUFLEN - 1, "Hello World (#%d)", i );
                        ANY_LOG( 5, "CLIENT: Test #6 - TCP sending data (#%d)", ANY_LOG_INFO, i );
                        IOChannel_write( stream, buffer, BUFLEN );
                        i++;
                    }

                    if( ( i != MSG_COUNT ) || ( IOChannel_isErrorOccurred( stream ) == true ) )
                    {
                        errorOccured = true;
                    }
                    ANY_LOG( 5, "CLIENT: Test #6 - TCP client stops talking", ANY_LOG_INFO );
                    IOChannel_close( stream );
                }
                IOChannel_clear( stream );
            }
            IOChannel_delete( stream );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }

    return (void *)NULL;
}


// For Test_UDP_ClientServer
void *udp_server( void *arg )
{
    IOChannel    *stream = (IOChannel *)NULL;
    const char   *url    = "ServerUdp://2222";
    char         buffer[BUFLEN];
    unsigned int i       = 0;
    long int     lnumber = 0;
    char         *pch    = (char *)NULL;
    int          status;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );


    stream = IOChannel_new();
    if( !IOChannel_init( stream ) )
    {
        ANY_LOG( 5, "SERVER: Test #7 - UDP server init failed...", ANY_LOG_INFO );
        errorOccured = true;
    }
    else
    {
        /* Reading string Data */
        ANY_LOG( 5, "SERVER: Test #7 - UDP server starts listening...", ANY_LOG_INFO );

        /* Let the test case start the client thread */
        Cond_signal( mutexAndCond->cond );

        status = Mutex_unlock( mutexAndCond->mutex );
        ANY_REQUIRE( status == 0 );

        if( IOChannel_open( stream, url, IOCHANNEL_MODE_RW, IOCHANNEL_PERMISSIONS_ALL ) != true )
        {
            ANY_LOG( 5, "SERVER: Test #7 - UDP server channel opening failed...", ANY_LOG_INFO );
            errorOccured = true;
        }
        else
        {
            lnumber = IOChannel_getIsReadDataAvailableTimeout( stream );
            ANY_LOG( 5, "SERVER: Test #7 - UDP server current timeout for read is( usecs ): [%ld]", ANY_LOG_INFO,
                     lnumber );

            ANY_LOG( 5, "SERVER: Test #7 - UDP server changing timeout for read to 1500 usecs", ANY_LOG_INFO );
            IOChannel_setIsReadDataAvailableTimeout( stream, 1500 );

            // Check that the change was effective
            lnumber = IOChannel_getIsReadDataAvailableTimeout( stream );
            if( lnumber != 1500 )
            {
                errorOccured = true;
            }

            while( ( IOChannel_eof( stream ) == false ) && ( IOChannel_isErrorOccurred( stream ) == false ) &&
                   ( i < MSG_COUNT ) )
            {
                IOChannel_read( stream, buffer, BUFLEN );
                ANY_LOG( 5, "SERVER: Test #7 - UDP Received: %s", ANY_LOG_DATA, buffer );
                // Confirm that we received really one of our client messages
                pch = strstr( buffer, "Hello World" );
                if( pch == (char *)NULL )
                {
                    errorOccured = true;
                }
                i++;
            }

            if( ( i != MSG_COUNT ) || ( IOChannel_isErrorOccurred( stream ) == true ) )
            {
                ANY_LOG( 5, "SERVER: Test #7 - UDP server did not get all messages...", ANY_LOG_INFO );
                errorOccured = true;
            }

            ANY_LOG( 5, "SERVER: Test #7 - UDP server stops listening...", ANY_LOG_INFO );

            IOChannel_close( stream );
        }
        IOChannel_clear( stream );
    }
    IOChannel_delete( stream );


    return (void *)NULL;
}


// For Test_UDP_ClientServer
void *udp_client( void *arg )
{
    IOChannel    *stream   = (IOChannel *)NULL;
    const char   *url      = "Udp://127.0.0.1:2222";
    char         buffer[BUFLEN];
    unsigned int i         = 0;
    long int     lnumber   = 0;
    Cond         *condWait = (Cond *)NULL;


    // Used to be sure that the server up
    condWait = Cond_new();
    if( !condWait )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        stream = IOChannel_new();
        if( stream == (IOChannel *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !IOChannel_init( stream ) )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #7 - UDP client connecting to %s", ANY_LOG_INFO, url );

                if( IOChannel_open( stream, url, IOCHANNEL_MODE_RW, IOCHANNEL_PERMISSIONS_ALL ) == false )
                {
                    errorOccured = true;
                }
                else
                {
                    lnumber = IOChannel_getIsWritePossibleTimeout( stream );
                    ANY_LOG( 5, "CLIENT: Test #7 - UDP client current timeout for write is( usecs ): [%ld]",
                             ANY_LOG_INFO, lnumber );

                    ANY_LOG( 5, "CLIENT: Test #7 - UDP client changing timeout for write to 2000 usecs", ANY_LOG_INFO );
                    IOChannel_setIsWritePossibleTimeout( stream, 2000 );

                    // Check that the change was effective
                    lnumber = IOChannel_getIsWritePossibleTimeout( stream );
                    if( lnumber != 2000 )
                    {
                        errorOccured = true;
                    }

                    ANY_LOG( 5, "CLIENT: Test #7 - UDP client starts talking", ANY_LOG_INFO );

                    while( ( IOChannel_eof( stream ) == false ) && ( IOChannel_isErrorOccurred( stream ) == false ) &&
                           ( i < MSG_COUNT ) )
                    {
                        Any_snprintf( buffer, BUFLEN - 1, "Hello World (#%d)", i );
                        ANY_LOG( 5, "CLIENT: Test #7 - UDP sending data (#%d)", ANY_LOG_INFO, i );
                        IOChannel_write( stream, buffer, BUFLEN );
                        i++;
                    }

                    if( ( i != MSG_COUNT ) || ( IOChannel_isErrorOccurred( stream ) == true ) )
                    {
                        errorOccured = true;
                    }
                    ANY_LOG( 5, "CLIENT: Test #7 - UDP client stops talking", ANY_LOG_INFO );
                    IOChannel_close( stream );
                }
                IOChannel_clear( stream );
            }
            IOChannel_delete( stream );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }

    return (void *)NULL;
}


// For Test_UDP_Broadcast
void *udp_broadcast_server( void *arg )
{
    IOChannel *stream      = (IOChannel *)NULL;
    char      msg[MSG_LEN] = "";
    char      *pch         = (char *)NULL;
    int       status;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );

    stream     = IOChannel_new();
    if( stream == (IOChannel *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !IOChannel_init( stream ) )
        {
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "SERVER: Test #8 - UDP broadcast server: binding to UDP port 4000...", ANY_LOG_INFO );

            /* Let the test case start the client thread */
            Cond_signal( mutexAndCond->cond );

            status = Mutex_unlock( mutexAndCond->mutex );
            ANY_REQUIRE( status == 0 );

            if( IOChannel_openFromString( stream,
                                          "stream=ServerUdp port=4000 broadcast=true mode='IOCHANNEL_MODE_RW'" ) ==
                false )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "SERVER: Test #8 - UDP broadcast server: listening for incoming UDP...", ANY_LOG_INFO );

                while( IOChannel_isReadDataAvailable( stream ) == true &&
                       ( IOChannel_isErrorOccurred( stream ) == false ) )
                {
                    IOChannel_read( stream, msg, MSG_LEN );
                    ANY_LOG( 5, "SERVER: Test #8 - UDP broadcast server: Received= '%s'", ANY_LOG_INFO, msg );
                    pch = strstr( msg, "Hello " );
                    if( pch == (char *)NULL )
                    {
                        errorOccured = true;
                    }
                }
                if( IOChannel_isErrorOccurred( stream ) == true )
                {
                    errorOccured = true;
                }
                IOChannel_close( stream );
            }
            IOChannel_clear( stream );
        }
        IOChannel_delete( stream );
    }
    return (void *)NULL;
}


// For Test_UDP_Broadcast
void *udp_broadcast_client( void *arg )
{
    IOChannel *stream      = (IOChannel *)NULL;
    char      msg[MSG_LEN] = "";
    int       count;
    Cond      *condWait    = (Cond *)NULL;

    /* Wait to be sure that the server up */
    condWait   = Cond_new();
    if( condWait == (Cond *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        stream = IOChannel_new();
        if( stream == (IOChannel *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !IOChannel_init( stream ) )
            {
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #8 - sending UDP message to port 4000", ANY_LOG_INFO );
                if( !IOChannel_openFromString( stream,
                                               "stream=Udp host=192.168.2.255 port=4000 srcport=4001 mode='IOCHANNEL_MODE_RW' broadcast=true" ) )
                {
                    errorOccured = true;
                }
                else
                {
                    for( count = 0; count < NUM_MSG; count++ )
                    {
                        Any_sprintf( msg, "Hello %02d!", count );
                        IOChannel_write( stream, msg, MSG_LEN );
                        if( IOChannel_isErrorOccurred( stream ) )
                        {
                            errorOccured = true;
                        }
                    }
                    IOChannel_close( stream );
                }
                IOChannel_clear( stream );
            }
            IOChannel_delete( stream );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }
    return (void *)NULL;
}


// For Test_TCP_Block
void *blockNetworkTest_TCP_serverThread( void *arg )
{
    BerkeleySocketServer *serverBerkeleySocket = (BerkeleySocketServer *)NULL;
    BerkeleySocket       *newBerkeleySocket    = (BerkeleySocket *)NULL;
    BerkeleySocketType   proto                 = BERKELEYSOCKET_TCP;
    int                  serverPort            = 60002;
    int                  maxClient             = 5;
    char                 *remoteIp;
    char                 hostname[256];
    int                  status;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );


    ANY_LOG( 5, "SERVER: Test #9 - Using default protocol: TCP on server port %d", ANY_LOG_INFO, serverPort );

    serverBerkeleySocket = BerkeleySocketServer_new();
    if( serverBerkeleySocket == (BerkeleySocketServer *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !BerkeleySocketServer_init( serverBerkeleySocket, NULL ) )
        {
            ANY_LOG( 5, "SERVER: Test #9 - Unable to initialize a SockeServer", ANY_LOG_FATAL );
            errorOccured = true;
        }
        else
        {

            BerkeleySocket *sock = BerkeleySocketServer_getSocket( serverBerkeleySocket );
            BerkeleySocket_setReuseAddr( sock, true );

            if( BerkeleySocketServer_connect( serverBerkeleySocket, proto, serverPort, maxClient ) == NULL )
            {
                Cond_signal( mutexAndCond->cond );

                status = Mutex_unlock( mutexAndCond->mutex );
                ANY_REQUIRE( status == 0 );

                ANY_LOG( 5, "SERVER: Test #9 - Unable to connect the server", ANY_LOG_FATAL );
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "SERVER: Test #9 - Waiting for a client ...", ANY_LOG_INFO );

                /* Let the test case start the client thread */
                Cond_signal( mutexAndCond->cond );

                status = Mutex_unlock( mutexAndCond->mutex );
                ANY_REQUIRE( status == 0 );

                /* waits an incoming client */
                if( !BerkeleySocketServer_waitClient( serverBerkeleySocket, BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) ) )
                {
                    ANY_LOG( 5, "SERVER: Test #9 - No incoming client, quitting!!!", ANY_LOG_INFO );
                    errorOccured = true;
                }
                else
                {
                    ANY_LOG( 5, "SERVER: Test #9 - New client is waiting for us, creating a new socket ...",
                             ANY_LOG_INFO );

                    /* we go a new incoming connection so we create a socket for it */
                    newBerkeleySocket = BerkeleySocket_new();
                    if( newBerkeleySocket == (BerkeleySocket *)NULL )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        if( !BerkeleySocket_init( newBerkeleySocket ) )
                        {
                            errorOccured = true;
                        }
                        else
                        {
                            ANY_LOG( 5, "SERVER: Test #9 - Accepting the client ...", ANY_LOG_INFO );
                            BerkeleySocketServer_acceptClient( serverBerkeleySocket, newBerkeleySocket );
                            ANY_LOG( 5, "SERVER: Test #9 - Client accepted ...", ANY_LOG_INFO );

                            remoteIp = BerkeleySocket_getRemoteIp( newBerkeleySocket, hostname, 256 );
                            ANY_LOG( 5, "SERVER: Test #9 - Client ip is: %s", ANY_LOG_INFO, remoteIp );

                            /* sets the default timeout */
                            BerkeleySocket_setDefaultTimeout( newBerkeleySocket, BERKELEYSOCKET_TIMEOUT_DEFAULT );
                            ANY_LOG( 5, "SERVER: Test #9 - Waiting Client's data ...", ANY_LOG_INFO );
                            if( BerkeleySocket_isReadDataAvailable( newBerkeleySocket ) )
                            {
                                ANY_LOG( 5, "SERVER: Test #9 - Client's Data available ...", ANY_LOG_INFO );
                                blockNetworkTest_readBlock( newBerkeleySocket );
                            }
                            else
                            {
                                ANY_LOG( 5, "SERVER: Test #9 - No Client's data available ...", ANY_LOG_INFO );
                            }
                            ANY_LOG( 5, "SERVER: Test #9 - Waiting for 3 seconds", ANY_LOG_INFO );
                            Any_sleepSeconds( 3 );
                            /* close the remote connection */
                            ANY_LOG( 5, "SERVER: Test #9 - Disconnecting the Client ...", ANY_LOG_INFO );
                            BerkeleySocket_disconnect( newBerkeleySocket );
                        }
                        /* clear the socket */
                        ANY_LOG( 5, "SERVER: Test #9 - Clearing the Client ...", ANY_LOG_INFO );
                        BerkeleySocket_clear( newBerkeleySocket );
                    }
                    ANY_LOG( 5, "SERVER: Test #9 - Deleting the Client ...", ANY_LOG_INFO );
                    BerkeleySocket_delete( newBerkeleySocket );
                }
                ANY_LOG( 5, "SERVER: Test #9 - Closing the Server ...", ANY_LOG_INFO );
                BerkeleySocketServer_disconnect( serverBerkeleySocket );
            }
            ANY_LOG( 5, "SERVER: Test #9 - Clearing the Server ...", ANY_LOG_INFO );
            BerkeleySocketServer_clear( serverBerkeleySocket );
        }
        ANY_LOG( 5, "SERVER: Test #9 - Deleting the Server ...", ANY_LOG_INFO );
        BerkeleySocketServer_delete( serverBerkeleySocket );
    }

    return (void *)NULL;
}


// For Test_TCP_Block
void *blockNetworkTest_TCP_clientThread( void *arg )
{
    BerkeleySocketClient *client     = (BerkeleySocketClient *)NULL;
    BerkeleySocket       *sock       = (BerkeleySocket *)NULL;
    char                 *serverName = (char *)"127.0.0.1";
    BerkeleySocketType   proto       = BERKELEYSOCKET_TCP;
    int                  serverPort  = 60002;
    char                 *serverIp   = NULL;
    char                 hostname[256];
    int                  size        = MAX_SIZE;


    ANY_LOG( 5, "CLIENT: Test #9 - Using default protocol: TCP on server '%s' port %d", ANY_LOG_INFO, serverName,
             serverPort );

    serverIp = BerkeleySocket_host2Addr( serverName, hostname, 256 );

    client = BerkeleySocketClient_new();
    if( client == (BerkeleySocketClient *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( !BerkeleySocketClient_init( client, NULL ) )
        {
            ANY_LOG( 5, "CLIENT: Test #9 - Unable to initialize the socket'", ANY_LOG_FATAL );
            errorOccured = true;
        }
        else
        {
            BerkeleySocket_setDefaultTimeout( BerkeleySocketClient_getSocket( client ),
                                              BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) );

            ANY_LOG( 5, "CLIENT: Test #9 - Try to connect to '%s:%d'", ANY_LOG_INFO, serverName, serverPort );
            sock = BerkeleySocketClient_connect( client, proto, serverIp, serverPort );

            if( sock == (BerkeleySocket *)NULL )
            {
                ANY_LOG( 5, "CLIENT: Test #9 - Connection error", ANY_LOG_FATAL );
                errorOccured = true;
            }
            else
            {
                blockNetworkTest_writeBlock( sock, size );
                ANY_LOG( 5, "CLIENT: Test #9 - Wait for 2 seconds", ANY_LOG_INFO );
                Any_sleepSeconds( 2 );
                ANY_LOG( 5, "CLIENT: Test #9 - Disconnect the client socket", ANY_LOG_INFO );
                BerkeleySocketClient_disconnect( client );
            }
            ANY_LOG( 5, "CLIENT: Test #9 - Clear the client socket", ANY_LOG_INFO );
            BerkeleySocketClient_clear( client );
        }
        ANY_LOG( 5, "CLIENT: Test #9 - Delete the client socket", ANY_LOG_INFO );
        BerkeleySocketClient_delete( client );
    }

    return (void *)NULL;
}


// For Test_TCP_Block
static void blockNetworkTest_readBlock( BerkeleySocket *newBerkeleySocket )
{
    int          blockSize     = 0;
    unsigned int status        = 0;
    int          *dataBlock    = (int *)NULL;
    int          *ptrDataBlock = (int *)NULL;
    int          i             = 0;
    int          byteLeft      = 0;

    status = BerkeleySocket_read( newBerkeleySocket, (BaseUI8 *)&blockSize, sizeof( int ) );

    if( status != sizeof( int ) )
    {
        ANY_LOG( 5, "SERVER: Test #9 - Unknown blockSize %d", ANY_LOG_WARNING, blockSize );
        errorOccured = true;
    }
    else
    {
        ANY_LOG( 5, "SERVER: Test #9 - Allocation space for %d integers", ANY_LOG_INFO, blockSize );
        ptrDataBlock = dataBlock = ANY_NTALLOC( blockSize, int );
        if( dataBlock == (int *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            byteLeft = blockSize * sizeof( int );

            while( byteLeft != 0 )
            {
                if( BerkeleySocket_isReadDataAvailable( newBerkeleySocket ) == false )
                {
                    ANY_LOG( 5, "SERVER: Test #9 - No more data available quitting ...", ANY_LOG_WARNING );
                    errorOccured = true;
                }
                else
                {
                    ANY_LOG( 5, "SERVER: Test #9 - Reading %d bytes from the BerkeleySocket", ANY_LOG_INFO, byteLeft );
                    status = BerkeleySocket_read( newBerkeleySocket, (BaseUI8 *)ptrDataBlock, byteLeft );
                    ANY_LOG( 5, "SERVER: Test #9 - Received %d bytes", ANY_LOG_INFO, status );

                    byteLeft -= status;
                    ptrDataBlock += status;
                }
            }

            /* block checking */
            for( i = 0; i < blockSize; i++ )
            {
                if( dataBlock[ i ] != i )
                {
                    ANY_LOG( 5, "SERVER: Test #9 - Wrong number in block position %d", ANY_LOG_FATAL, i );
                    errorOccured = true;
                    break;
                }
            }

            ANY_FREE( dataBlock );
        }
    }
}


// For Test_TCP_Block
static void blockNetworkTest_writeBlock( BerkeleySocket *myBerkeleySocket, int blockSize )
{
    int          *dataBlock = (int *)NULL;
    unsigned int status     = 0;
    int          i          = 0;

    dataBlock = ANY_NTALLOC( blockSize, int );
    if( dataBlock == (int *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        ANY_LOG( 5, "CLIENT: Test #9 - Filling up %d ints", ANY_LOG_INFO, blockSize );

        /* block filling */
        for( i = 0; i < blockSize; i++ )
        {
            dataBlock[ i ] = i;
        }

        ANY_LOG( 5, "CLIENT: Test #9 - Sending %d bytes for the header", ANY_LOG_INFO, (int)sizeof( blockSize ) );

        status = BerkeleySocket_write( myBerkeleySocket, (BaseUI8 *)&blockSize, sizeof( blockSize ) );

        if( status != sizeof( blockSize ) )
        {
            ANY_LOG( 5, "CLIENT: Test #9 - Problem while sending the blockSize", ANY_LOG_WARNING );
            errorOccured = true;
        }
        else
        {
            ANY_LOG( 5, "CLIENT: Test #9 - Sending %d bytes for %d ints", ANY_LOG_INFO,
                     (int)( blockSize * sizeof( int ) ), blockSize );
            status = BerkeleySocket_write( myBerkeleySocket, (BaseUI8 *)dataBlock, blockSize * sizeof( int ) );

            if( status != ( blockSize * sizeof( int ) ) )
            {
                ANY_LOG( 5, "CLIENT: Test #9 - Problem while sending the data", ANY_LOG_WARNING );
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "CLIENT: Test #9 - Block write done!!!", ANY_LOG_INFO );
            }
        }
        ANY_FREE( dataBlock );
    }
}


// For Test_Berkeley_Data
void *BerkeleyData_serverThread( void *arg )
{
    BerkeleySocketServer *serverBerkeleySocket = (BerkeleySocketServer *)NULL;
    BerkeleySocket       *socket               = (BerkeleySocket *)NULL;
    BerkeleySocket       *newBerkeleySocket    = (BerkeleySocket *)NULL;
    BerkeleySocketType   proto                 = BERKELEYSOCKET_TCP;
    int                  serverPort            = 60002;
    int                  maxClient             = 5;
    int                  status;

    MutexAndCondition *mutexAndCond;

    mutexAndCond = (MutexAndCondition *)arg;

    ANY_REQUIRE( mutexAndCond );
    ANY_REQUIRE( mutexAndCond->mutex );
    ANY_REQUIRE( mutexAndCond->cond );

    status = Mutex_lock( mutexAndCond->mutex );
    ANY_REQUIRE( status == 0 );


    ANY_LOG( 5, "SERVER: Test #11 - Using TCP protocol on server port %d", ANY_LOG_INFO, serverPort );

    serverBerkeleySocket = BerkeleySocketServer_new();
    if( serverBerkeleySocket == (BerkeleySocketServer *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        if( BerkeleySocketServer_init( serverBerkeleySocket, NULL ) == false )
        {
            ANY_LOG( 5, "SERVER: Test #11 - Unable to initialize a SockeServer", ANY_LOG_FATAL );
            errorOccured = true;
        }
        else
        {
            socket = BerkeleySocketServer_getSocket( serverBerkeleySocket );
            BerkeleySocket_setReuseAddr( socket, true );

            if( BerkeleySocketServer_connect( serverBerkeleySocket, proto, serverPort, maxClient ) == NULL )
            {
                ANY_LOG( 5, "SERVER: Test #11 - Unable to connect the server", ANY_LOG_FATAL );
                errorOccured = true;
            }
            else
            {
                ANY_LOG( 5, "SERVER: Test #11 - Waiting for a client ...", ANY_LOG_INFO );
                /* Let the test case start the client thread */
                Cond_signal( mutexAndCond->cond );

                status = Mutex_unlock( mutexAndCond->mutex );
                ANY_REQUIRE( status == 0 );

                if( BerkeleySocketServer_waitClient( serverBerkeleySocket, BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) ) ==
                    false )
                {
                    ANY_LOG( 5, "SERVER: Test #11 - No incoming client, quitting!!!", ANY_LOG_INFO );
                    errorOccured = true;
                }
                else
                {
                    ANY_LOG( 5, "SERVER: Test #11 - New client is waiting for us, creating a new socket ...",
                             ANY_LOG_INFO );

                    /* we go a new incoming connection so we create a socket for it */
                    newBerkeleySocket = BerkeleySocket_new();
                    if( newBerkeleySocket == (BerkeleySocket *)NULL )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        BerkeleySocket_init( newBerkeleySocket );

                        ANY_LOG( 5, "SERVER: Test #11 - Accepting the client ...", ANY_LOG_INFO );
                        BerkeleySocketServer_acceptClient( serverBerkeleySocket, newBerkeleySocket );
                        ANY_LOG( 5, "SERVER: Test #11 - Client accepted ...", ANY_LOG_INFO );

                        /* sets the default timeout */
                        BerkeleySocket_setDefaultTimeout( newBerkeleySocket, BERKELEYSOCKET_TIMEOUT_DEFAULT );
                        ANY_LOG( 5, "SERVER: Test #11 - Waiting Client's data ...", ANY_LOG_INFO );
                        if( BerkeleySocket_isReadDataAvailable( newBerkeleySocket ) == true )
                        {
                            ANY_LOG( 5, "SERVER: Test #11 - Client's Data available ...", ANY_LOG_INFO );
                            if( BerkeleyData_readString( newBerkeleySocket ) == false )
                            {
                                errorOccured = true;
                            }
                            if( BerkeleyData_readInteger( newBerkeleySocket ) == false )
                            {
                                errorOccured = true;
                            }
                            if( BerkeleyData_readFloat( newBerkeleySocket ) == false )
                            {
                                errorOccured = true;
                            }
                            if( BerkeleyData_readDouble( newBerkeleySocket ) == false )
                            {
                                errorOccured = true;
                            }
                        }
                        else
                        {
                            ANY_LOG( 5, "SERVER: Test #11 - No Client's data available ...", ANY_LOG_INFO );
                            errorOccured = true;
                        }
                        ANY_LOG( 5, "SERVER: Test #11 - Disconnecting the Client ...", ANY_LOG_INFO );

                        BerkeleySocket_disconnect( newBerkeleySocket );
                        BerkeleySocket_clear( newBerkeleySocket );
                        BerkeleySocket_delete( newBerkeleySocket );
                    }
                }
                BerkeleySocketServer_disconnect( serverBerkeleySocket );
            }
            ANY_LOG( 5, "SERVER: Test #11 - Closing the Server ...", ANY_LOG_INFO );
            BerkeleySocketServer_clear( serverBerkeleySocket );
        }
        BerkeleySocketServer_delete( serverBerkeleySocket );
    }
    return (void *)NULL;
}


// For Test_Berkeley_Data
void *BerkeleyData_clientThread( void *arg )
{
    BerkeleySocketClient *client     = (BerkeleySocketClient *)NULL;
    BerkeleySocket       *sock       = (BerkeleySocket *)NULL;
    char                 *serverName = (char *)"127.0.0.1";
    BerkeleySocketType   proto       = BERKELEYSOCKET_TCP;
    int                  serverPort  = 60002;
    char                 *serverIp   = NULL;
    bool                 swapBytes   = false;
    char                 hostname[256];
    Cond                 *condWait   = (Cond *)NULL;


    condWait = Cond_new();
    if( condWait == (Cond *)NULL )
    {
        errorOccured = true;
    }
    else
    {
        Cond_init( condWait, COND_PRIVATE );
        Cond_wait( condWait, ( 1 * 1000 * 1000 ) );

        ANY_LOG( 5, "CLIENT: Test #11 - Using TCP protocol on server '%s' port %d", ANY_LOG_INFO, serverName,
                 serverPort );

        client = BerkeleySocketClient_new();
        if( client == (BerkeleySocketClient *)NULL )
        {
            errorOccured = true;
        }
        else
        {
            if( !BerkeleySocketClient_init( client, NULL ) )
            {
                ANY_LOG( 5, "CLIENT: Test #11 - Unable to initialize the socket'", ANY_LOG_FATAL );
                errorOccured = true;
            }
            else
            {
                serverIp = BerkeleySocket_host2Addr( serverName, hostname, 256 );
                if( serverIp == NULL )
                {
                    errorOccured = true;
                }
                else
                {
                    BerkeleySocket_setDefaultTimeout( BerkeleySocketClient_getSocket( client ),
                                                      BERKELEYSOCKET_TIMEOUT_SECONDS( 10 ) );

                    ANY_LOG( 5, "CLIENT: Test #11 - Try to connect to '%s(ip=%s):%d'", ANY_LOG_INFO, serverName,
                             serverIp, serverPort );
                    sock = BerkeleySocketClient_connect( client, proto, serverIp, serverPort );
                    if( sock == (BerkeleySocket *)NULL )
                    {
                        errorOccured = true;
                    }
                    else
                    {
                        BerkeleySocket_setLinger( sock, false, BERKELEYSOCKET_LINGERTIMEOUT_DEFAULT );

                        if( !BerkeleyData_writeString( sock ) )
                        {
                            errorOccured = true;
                        }
                        if( !BerkeleyData_writeInteger( sock, swapBytes ) )
                        {
                            errorOccured = true;
                        }
                        if( !BerkeleyData_writeFloat( sock, swapBytes ) )
                        {
                            errorOccured = true;
                        }
                        if( !BerkeleyData_writeDouble( sock, swapBytes ) )
                        {
                            errorOccured = true;
                        }

                        BerkeleySocketClient_disconnect( client );
                    }
                }
                BerkeleySocketClient_clear( client );
            }
            BerkeleySocketClient_delete( client );
        }
        Cond_clear( condWait );
        Cond_delete( condWait );
    }
    return (void *)NULL;
}


// For Test_Berkeley_Data
bool BerkeleyData_readString( BerkeleySocket *newBerkeleySocket )
{
    char a_string[12];
    int  status = 0;
    bool retVal = true;
    char *pch   = (char *)NULL;

    Any_memset( (void *)a_string, 0, 12 );

    status = BerkeleySocket_read( newBerkeleySocket, (BaseUI8 *)a_string, 11 * sizeof( char ) );

    if( status <= 0 )
    {
        ANY_LOG( 5, "SERVER: Test #11 - Problem while receiving string [%s] (should be [Hello world])", ANY_LOG_WARNING,
                 a_string );
        retVal = false;
    }
    else
    {
        pch = strstr( a_string, "Hello world" );
        if( pch == (char *)NULL )
        {
            ANY_LOG( 5, "SERVER: Test #11 - Problem while comparing string [%s] (should be [Hello world])",
                     ANY_LOG_WARNING, a_string );
            retVal = false;
        }
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_readInteger( BerkeleySocket *newBerkeleySocket )
{
    int  an_integer = 0;
    int  status     = 0;
    bool retVal     = true;

    status = BerkeleySocket_read( newBerkeleySocket, (BaseUI8 *)&an_integer, sizeof( int ) );
    if( ( status < (int)sizeof( int ) ) || ( an_integer != 1034 ) )
    {
        ANY_LOG( 5, "SERVER: Test #11 - Problem while receiving int [%d] (should be [1034])", ANY_LOG_WARNING,
                 an_integer );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_readFloat( BerkeleySocket *newBerkeleySocket )
{
    float a_float = 0;
    int   status  = 0;
    bool  retVal  = true;

    status = BerkeleySocket_read( newBerkeleySocket, (BaseUI8 *)&a_float, sizeof( float ) );
    if( status < (int)sizeof( float ) || a_float < (float)12.34 || a_float > (float)12.34 )
    {
        ANY_LOG( 0, "SERVER: Test #11 - Problem while receiving float [%f] (should be [12.340000])", ANY_LOG_WARNING,
                 a_float );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_readDouble( BerkeleySocket *newBerkeleySocket )
{
    double a_double = 0;
    int    status   = 0;
    bool   retVal   = true;

    status = BerkeleySocket_read( newBerkeleySocket, (BaseUI8 *)&a_double, sizeof( double ) );

    if( status < (int)sizeof( double ) || a_double < (double)12.34 || a_double > (double)12.4 )
    {
        ANY_LOG( 0, "SERVER: Test #11 - Problem while receiving double [%f] (should be [12.340600])", ANY_LOG_WARNING,
                 a_double );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_writeString( BerkeleySocket *myBerkeleySocket )
{
    char *a_string = (char *)"Hello world";
    int  status    = 0;
    bool retVal    = true;

    ANY_LOG( 5, "CLIENT: Test #11 - Sending string: %s", ANY_LOG_INFO, a_string );

    status = BerkeleySocket_write( myBerkeleySocket, (BaseUI8 *)a_string, Any_strlen( a_string ) * sizeof( char ) );

    if( status < (int)Any_strlen( a_string ) * (int)sizeof( char ) )
    {
        ANY_LOG( 5, "CLIENT: Test #11 - Problem found trying to send the string (status=%d)", ANY_LOG_INFO, status );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_writeInteger( BerkeleySocket *myBerkeleySocket, bool swapBytes )
{
    int  an_integer = 1034;
    int  status     = 0;
    bool retVal     = true;

    ANY_LOG( 5, "CLIENT: Test #11 - Sending int: %d", ANY_LOG_INFO, an_integer );

    if( swapBytes )
    {
        BerkeleyData_swapByteOrder( (char *)&an_integer, sizeof( int ) );
    }

    status = BerkeleySocket_write( myBerkeleySocket, (BaseUI8 *)&an_integer, sizeof( int ) );

    if( status < (int)sizeof( int ) )
    {
        ANY_LOG( 5, "CLIENT: Test #11 - Problem found trying to send the int (status=%d)", ANY_LOG_INFO, status );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_writeFloat( BerkeleySocket *myBerkeleySocket, bool swapBytes )
{
    float a_float = 12.34;
    int   status  = 0;
    bool  retVal  = true;

    ANY_LOG( 5, "CLIENT: Test #11 - Sending float: %f", ANY_LOG_INFO, a_float );

    if( swapBytes )
    {
        BerkeleyData_swapByteOrder( (char *)&a_float, sizeof( float ) );
    }

    status = BerkeleySocket_write( myBerkeleySocket, (BaseUI8 *)&a_float, sizeof( float ) );

    if( status < (int)sizeof( float ) )
    {
        ANY_LOG( 5, "CLIENT: Test #11 - Problem found trying to send the float (status=%d)", ANY_LOG_INFO, status );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
bool BerkeleyData_writeDouble( BerkeleySocket *myBerkeleySocket, bool swapBytes )
{
    double a_double = 12.3406;
    int    status   = 0;
    bool   retVal   = true;

    ANY_LOG( 5, "CLIENT: Test #11 - Sending double: %f", ANY_LOG_INFO, a_double );

    if( swapBytes )
    {
        BerkeleyData_swapByteOrder( (char *)&a_double, sizeof( double ) );
    }

    status = BerkeleySocket_write( myBerkeleySocket, (BaseUI8 *)&a_double, sizeof( double ) );

    if( status < (int)sizeof( double ) )
    {
        ANY_LOG( 5, "CLIENT: Test #11 - Problem found trying to send the double (status=%d)", ANY_LOG_INFO, status );
        retVal = false;
    }

    return retVal;
}


// For Test_Berkeley_Data
void BerkeleyData_swapByteOrder( char *data, int len )
{
    int  i       = 0;
    int  halfLen = len >> 1;
    char tmp;

    for( i = 0; i < halfLen; ++i )
    {
        tmp = data[ i ];
        data[ i ]           = data[ len - i - 1 ];
        data[ len - i - 1 ] = tmp;
    }
}


/*---------------------------------------------------------------------------*/
/* Main program                                                              */
/*---------------------------------------------------------------------------*/
int main( void )
{
    CuSuite  *suite   = CuSuiteNew();
    CuString *output  = CuStringNew();
    char     *verbose = (char *)NULL;

    ANY_REQUIRE( suite );
    ANY_REQUIRE( output );

    verbose = getenv( (char *)"VERBOSE" );
    if( verbose != NULL && Any_strcmp( verbose, (char *)"TRUE" ) == 0 )
    {
        Any_setDebugLevel( 10 );
    }
    else
    {
        Any_setDebugLevel( 0 );
    }

    SUITE_ADD_TEST( suite, Test_IOChannel_ClientServer_01 );
    SUITE_ADD_TEST( suite, Test_IOChannel_ClientServer_02 );
    SUITE_ADD_TEST( suite, Test_IOChannel_ClientServer_03 );
    SUITE_ADD_TEST( suite, Test_IOChannel_ClientServer_04 );
    SUITE_ADD_TEST( suite, Test_IOChannel_MultiClientServer );
    SUITE_ADD_TEST( suite, Test_TCP_ClientServer );
    SUITE_ADD_TEST( suite, Test_UDP_ClientServer );
    SUITE_ADD_TEST( suite, Test_UDP_Broadcast );
    SUITE_ADD_TEST( suite, Test_TCP_Block );
    SUITE_ADD_TEST( suite, Test_Berkeley_Timeouts );
    SUITE_ADD_TEST( suite, Test_Berkeley_Data );
    SUITE_ADD_TEST( suite, Test_IOChannel_openTcp );
    SUITE_ADD_TEST( suite, Test_IOChannel_printf );
    SUITE_ADD_TEST( suite, Test_NameResolv );

    CuSuiteRun( suite );
    CuSuiteSummary( suite, output );
    CuSuiteDetails( suite, output );

    Any_fprintf( stderr, "%s\n", output->buffer );

    CuSuiteDelete( suite );
    CuStringDelete( output );


    return suite->failCount;
}
