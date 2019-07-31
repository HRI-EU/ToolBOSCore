/*
 *  Unittest for MTList and MTMessageQueue
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
#include <MTList.h>
#include <MTQueue.h>
#include <PQueue.h>
#include <PQueueArray.h>
#include <Threads.h>

#include <CuTest.h>

#if defined(__windows__)
#define TOOLBOSLIBRARY "ToolBOSCore.2.0.dll"
#else
#define TOOLBOSLIBRARY "libToolBOSCore.so"
#endif


/*---------------------------------------------------------------------------*/
/* Defines                                                                   */
/*---------------------------------------------------------------------------*/


#define NUMELEMENTS 10


/*---------------------------------------------------------------------------*/
/* MTList                                                                    */
/*---------------------------------------------------------------------------*/


void Test_MTList_lifecycle( CuTest *tc )
{
    MTList *l = (MTList *)NULL;
    l = MTList_new();
    CuAssertPtrNotNull( tc, l );

    MTList_init( l );
    MTList_clear( l );
    CuAssertPtrNotNull( tc, l );

    MTList_delete( l );
}


void Test_MTList_main( CuTest *tc )
{
    char *element10 = (char *)"10. element";
    MTList *l = NULL;
    char *element;

    l = MTList_new();
    CuAssertPtrNotNull( tc, l );

    MTList_init( l );
    MTList_setDeleteMode( l, MTLIST_DELETEMODE_MANUAL );

    MTList_insert( l, (char *)"2. element" );
    MTList_insert( l, (char *)"1. element" );

    ANY_LOG( 3, "List content...", ANY_LOG_INFO );
    MTLIST_FOREACH_BEGIN ( l, MTLIST_ITERATE_FOR_READ )
                {
                    ANY_LOG( 3, "Element: %s", ANY_LOG_INFO, (char *)MTLIST_FOREACH_ELEMENTPTR );
                }
    MTLIST_FOREACH_END;

    ANY_LOG( 3, "Test isPresent() function...", ANY_LOG_INFO );

    if( MTList_isPresent( l, (void *)element10 ) == true )
    {
        ANY_LOG( 3, "'%s' is present in the List", ANY_LOG_INFO, element10 );
    }
    else
    {
        ANY_LOG( 3, "'%s' is not present in the list", ANY_LOG_INFO, element10 );
    }

    MTList_add( l, element10 );

    if( MTList_isPresent( l, (void *)element10 ) == true )
    {
        ANY_LOG( 3, "'%s' is present in the List", ANY_LOG_INFO, element10 );
    }
    else
    {
        ANY_LOG( 3, "'%s' is not present in the list", ANY_LOG_INFO, element10 );
    }

    ANY_LOG( 3, "List content...", ANY_LOG_INFO );
    MTLIST_FOREACH_BEGIN ( l, MTLIST_ITERATE_FOR_READ )
                {
                    ANY_LOG( 3, "Element: %s", ANY_LOG_INFO, (char *)MTLIST_FOREACH_ELEMENTPTR );
                }
    MTLIST_FOREACH_END;

    MTList_remove( l, (int ( * )( void *, void * ))strcmp, (void *)element10 );

    ANY_LOG( 3, "------------------------------------", ANY_LOG_INFO );


    MTList_add( l, (char *)"3. element" );
    MTList_add( l, (char *)"4. element" );
    MTList_add( l, (char *)"5. element" );
    MTList_insert( l, (char *)"0. element" );

    ANY_LOG( 3, "BREAK List test...", ANY_LOG_INFO );
    MTLIST_FOREACH_BEGIN ( l, MTLIST_ITERATE_FOR_READ )
                {
                    ANY_LOG( 3, "Element: %s", ANY_LOG_INFO, (char *)MTLIST_FOREACH_ELEMENTPTR );

                    MTLIST_FOREACH_BREAK;
                }
    MTLIST_FOREACH_END;

    ANY_LOG( 3, "List content...", ANY_LOG_INFO );
    MTLIST_FOREACH_BEGIN ( l, MTLIST_ITERATE_FOR_READ )
                {
                    ANY_LOG( 3, "Element: %s", ANY_LOG_INFO, (char *)MTLIST_FOREACH_ELEMENTPTR );
                }
    MTLIST_FOREACH_END;

    element = (char *)"1. element";

    ANY_LOG( 3, "Removing element: %s", ANY_LOG_INFO, element );
    MTList_remove( l, (int ( * )( void *, void * ))strcmp, (void *)element );

    ANY_LOG( 3, "List content...", ANY_LOG_INFO );
    MTLIST_FOREACH_BEGIN ( l, MTLIST_ITERATE_FOR_READ )
                {
                    ANY_LOG( 3, "Element: %s", ANY_LOG_INFO, (char *)MTLIST_FOREACH_ELEMENTPTR );
                }
    MTLIST_FOREACH_END;

    ANY_LOG( 3, "List content with FOREACH_NOLOCK...", ANY_LOG_INFO );
    MTLIST_FOREACH_NOLOCK_BEGIN ( l )
            {
                ANY_LOG( 3, "Element: %s", ANY_LOG_INFO, (char *)MTLIST_FOREACH_ELEMENTPTR );
            }
    MTLIST_FOREACH_NOLOCK_END;

    MTList_clear( l );
    MTList_delete( l );
}


/*---------------------------------------------------------------------------*/
/* MTQueue                                                                   */
/*---------------------------------------------------------------------------*/


typedef struct Point
{
    int posX;
    int posY;
}
        Point;


Point *Point_new( void );

int Point_init( Point *self, int posX, int posY );

void Point_clear( Point *self );

void Point_delete( Point *self );


Point *Point_new( void )
{
    Point *self = ANY_TALLOC( Point );
    ANY_REQUIRE( self );

    return ( self );
}


int Point_init( Point *self, int posX, int posY )
{
    ANY_REQUIRE( self );

    self->posX = posX;
    self->posY = posY;

    return ( 0 );
}


void Point_clear( Point *self )
{
    ANY_REQUIRE( self );
}


void Point_delete( Point *self )
{
    ANY_REQUIRE( self );

    ANY_FREE( self );
}


void Test_MTQueue( CuTest *tc )
{
    ANY_REQUIRE( tc );

    int i = 0;
    MTQueue *queue = NULL;
    Point *p = NULL;

    ANY_LOG( 3, "Allocating a new MTQueue", ANY_LOG_INFO );
    queue = MTQueue_new();

    ANY_LOG( 3, "Initializing the queue FIFO without multithreading", ANY_LOG_INFO );
    MTQueue_init( queue, MTQUEUE_FIFO, false );

    ANY_LOG( 3, "Push '%d' Points in the queue", ANY_LOG_INFO, NUMELEMENTS );

    for( i = 0; i < NUMELEMENTS; i++ )
    {
        p = Point_new();
        ANY_REQUIRE( p );

        Point_init( p, i, i * 2 );

        ANY_LOG( 3, "Setting posX = %d", ANY_LOG_INFO, i );

        MTQueue_push( queue, (void *)p, MTQUEUE_NOCLASS );
    }

    ANY_LOG( 3, "The queue containts '%ld' elements", ANY_LOG_INFO, MTQueue_numElements( queue ));

    ANY_LOG( 3, "Now popping up all the elements from the queue. The elements must be in sequence", ANY_LOG_INFO );

    for( i = 0; i < NUMELEMENTS; i++ )
    {
        p = (Point *)MTQueue_pop( queue, NULL );
        ANY_REQUIRE( p );

        ANY_LOG( 3, "Getting posX = %d", ANY_LOG_INFO, p->posX );

        Point_clear( p );
        Point_delete( p );
    }

    ANY_LOG( 3, "The queue containts '%ld' elements", ANY_LOG_INFO, MTQueue_numElements( queue ));

    ANY_LOG( 3, "Destroying the MTQueue", ANY_LOG_INFO );

    MTQueue_clear( queue );
    MTQueue_delete( queue );
}


/*---------------------------------------------------------------------------*/
/* PQueue                                                                    */
/*---------------------------------------------------------------------------*/


void Test_PQueue( CuTest *tc )
{
    int i = 0;
    PQueue *queue = NULL;
    Base2DI32 point = { 0, 0 };

    ANY_LOG( 3, "Allocating a new PQueue", ANY_LOG_INFO );
    queue = PQueue_new();

    ANY_LOG( 3, "Initializing queue", ANY_LOG_INFO );

    // For initialization, the type-name and the library where to find it have to be provided.
    // The type should have a serialize() and indirectSerialize() fuction!
    CuAssertTrue( tc, PQueue_init( queue,
                                   NUMELEMENTS,
                                   "Base2DI32",
                                   TOOLBOSLIBRARY ) == PQueue_ok );

    // setupElement() checks the size of the type and allocates memory appropriately.
    CuAssertTrue( tc, PQueue_setupElement( queue, (void *)( &point )) == PQueue_ok );

    ANY_LOG( 3, "Push '%d' Points in the queue", ANY_LOG_INFO, NUMELEMENTS );

    for( i = 0; i < NUMELEMENTS; i++ )
    {
        point.x = i;
        point.y = 2 * i + 1;

        ANY_LOG( 3, "Setting posX = %d posY = %d", ANY_LOG_INFO, point.x, point.y );

        // simple pushing
        if( PQueue_push( queue, (void *)( &point )) != PQueue_ok )
        {
            ANY_LOG( 3, "Unable to push element on queue!", ANY_LOG_FATAL );
        }
    }

    ANY_LOG( 3, "The queue contains '%d' elements", ANY_LOG_INFO, PQueue_numElements( queue ));

    ANY_LOG( 3, "Now popping up all the elements from the queue. The elements must be in sequence", ANY_LOG_INFO );

    for( i = 0; i < NUMELEMENTS; i++ )
    {
        // popping stores the element in the memory pointed to by the second argument (here: &point)
        if( PQueue_pop( queue, (void *)( &point )) != PQueue_ok )
        {
            ANY_LOG( 3, "Unable to pop element from queue!", ANY_LOG_FATAL );
        }

        ANY_LOG( 3, "Getting posX = %d posY = %d", ANY_LOG_INFO, point.x, point.y );

    }

    ANY_LOG( 3, "The queue contains '%d' elements", ANY_LOG_INFO, PQueue_numElements( queue ));

    ANY_LOG( 3, "Destroying the PQueue", ANY_LOG_INFO );

    PQueue_clear( queue );
    PQueue_delete( queue );
}


/*---------------------------------------------------------------------------*/
/* PQueueArray                                                               */
/*---------------------------------------------------------------------------*/


typedef struct DataStruct
{
    BaseBool quit;
    PQueueArray *queue;
    BaseBool thread1Running;
    BaseBool thread2Running;
    BaseBool thread3Running;
    BaseF32 thresh1;
    BaseF32 thresh2;
    BaseF32 thresh3;
} DataStruct;


void *Example_producer( void *data )
{
    DataStruct *dataStruct = NULL;
    Base2DI32 point = { 0, 0 };
    BaseF32 roll = 0.0;
    PQueueStatus status = PQueue_ok;

    dataStruct = (DataStruct *)data;

    while( dataStruct->quit == false )
    {
        point.x = rand() % 100;
        point.y = rand() % 100;
        roll = ((BaseF32)rand()) / ((BaseF32)RAND_MAX );
        if( roll >= dataStruct->thresh1 )
        {
            // push point onto queue #0 and queue #1
            status = PQueueArray_push( dataStruct->queue, 0, (void *)( &point ));
            switch( status )
            {
                case PQueue_ok:
                    break;
                case PQueue_storeDataFailed:
                    ANY_LOG( 3, "Store data failed!", ANY_LOG_ERROR );
                    break;
                case PQueue_queueFull:
                    ANY_LOG( 3, "Queue full!", ANY_LOG_WARNING );
                    break;
                default:
                    ANY_LOG( 3, "Unknown status %i!", ANY_LOG_ERROR, status );
                    break;
            }
            status = PQueueArray_push( dataStruct->queue, 1, (void *)( &point ));
            switch( status )
            {
                case PQueue_ok:
                    printf( "Producer Point: %i %i\n", point.x, point.y );
                    break;
                case PQueue_storeDataFailed:
                    ANY_LOG( 3, "Store data failed!", ANY_LOG_ERROR );
                    break;
                case PQueue_queueFull:
                    ANY_LOG( 3, "Queue full!", ANY_LOG_WARNING );
                    break;
                default:
                    ANY_LOG( 3, "Unknown status %i!", ANY_LOG_ERROR, status );
                    break;
            }
        }

        Any_sleepMilliSeconds( rand() % 100 );
    }

    dataStruct->thread1Running = false;

    return NULL;
}


void *Example_consumer0( void *data )
{
    DataStruct *dataStruct = NULL;
    Base2DI32 point = { 0, 0 };
    BaseF32 roll = 0.0;
    PQueueStatus status = PQueue_ok;

    dataStruct = (DataStruct *)data;

    while( dataStruct->quit == false )
    {
        roll = ((BaseF32)rand()) / ((BaseF32)RAND_MAX );
        if( roll >= dataStruct->thresh2 )
        {
            // popping stores the element in the memory pointed to by the second argument (here: &point)
            status = PQueueArray_pop( dataStruct->queue, 0, (void *)( &point ));
            switch( status )
            {
                case PQueue_ok:
                    printf( "Consumer #0 Point: %i %i\n", point.x, point.y );
                    break;
                case PQueue_retrieveDataFailed:
                    ANY_LOG( 3, "Retrieve data failed!", ANY_LOG_ERROR );
                    break;
                case PQueue_queueEmpty:
                    ANY_LOG( 3, "Queue empty!", ANY_LOG_WARNING );
                    break;
                default:
                    ANY_LOG( 3, "Unknown status %i!", ANY_LOG_ERROR, status );
                    break;
            }
        }

        Any_sleepMilliSeconds( rand() % 100 );
    }

    dataStruct->thread2Running = false;

    return NULL;
}


void *Example_consumer1( void *data )
{
    DataStruct *dataStruct = NULL;
    Base2DI32 point = { 0, 0 };
    BaseF32 roll = 0.0;
    PQueueStatus status = PQueue_ok;

    dataStruct = (DataStruct *)data;

    while( dataStruct->quit == false )
    {
        roll = ((BaseF32)rand()) / ((BaseF32)RAND_MAX );
        if( roll >= dataStruct->thresh3 )
        {
            // popping stores the element in the memory pointed to by the second argument (here: &point)
            status = PQueueArray_pop( dataStruct->queue, 1, (void *)( &point ));
            switch( status )
            {
                case PQueue_ok:
                    printf( "Consumer #1 Point: %i %i\n", point.x, point.y );
                    break;
                case PQueue_retrieveDataFailed:
                    ANY_LOG( 3, "Retrieve data failed!", ANY_LOG_ERROR );
                    break;
                case PQueue_queueEmpty:
                    ANY_LOG( 3, "Queue empty!", ANY_LOG_WARNING );
                    break;
                default:
                    ANY_LOG( 3, "Unknown status %i!", ANY_LOG_ERROR, status );
                    break;
            }
        }

        Any_sleepMilliSeconds( rand() % 100 );
    }

    dataStruct->thread3Running = false;

    return NULL;
}


void Test_PQueueArray( CuTest *tc )
{
    Threads *thread1 = NULL;
    Threads *thread2 = NULL;
    Threads *thread3 = NULL;
    DataStruct dataStruct = { false, NULL, false, false, false, 0.3, 0.3, 0.3 };
    Base2DI32 point = { 0, 0 };

    ANY_LOG( 3, "Allocating a new PQueue", ANY_LOG_INFO );
    dataStruct.queue = PQueueArray_new();

    ANY_LOG( 3, "Initializing queue", ANY_LOG_INFO );
    // For initialization, the type-name and the library where to find it have to be provided.
    // The type should have a serialize() and indirectSerialize() fuction!
    // Since we will have two consumers, we set the arraySize to two.
    CuAssertTrue( tc, PQueueArray_init( dataStruct.queue,
                                        2,
                                        NUMELEMENTS,
                                        "Base2DI32",
                                        TOOLBOSLIBRARY ) == PQueue_ok );

    // setupElement() checks the size of the type and allocates memory appropriately.
    CuAssertTrue( tc, PQueueArray_setupElement( dataStruct.queue,
                                                (void *)( &point )) == PQueue_ok );


    // set up producer and consumer-thread
    thread1 = Threads_new();
    Threads_init( thread1, false );

    thread2 = Threads_new();
    Threads_init( thread2, false );

    thread3 = Threads_new();
    Threads_init( thread3, false );


//     TO BE FINISHED:

//     Threads_start( thread1, Example_producer, (void*)(&dataStruct) );
//     dataStruct.thread1Running = true;
//     Threads_start( thread2, Example_consumer0, (void*)(&dataStruct) );
//     dataStruct.thread2Running = true;
//     Threads_start( thread3, Example_consumer1, (void*)(&dataStruct) );
//     dataStruct.thread3Running = true;
//
//
//     Any_sleepSeconds( 10 );
//
//     dataStruct.quit = true;
//     while ( ( dataStruct.thread1Running == true ) ||
//             ( dataStruct.thread2Running == true ) ||
//             ( dataStruct.thread3Running == true ) );
//
//     ANY_LOG( 3, "Destroying the PQueue", ANY_LOG_INFO );

    PQueueArray_clear( dataStruct.queue );
    PQueueArray_delete( dataStruct.queue );

    Threads_clear( thread1 );
    Threads_delete( thread1 );
    Threads_clear( thread2 );
    Threads_delete( thread2 );
    Threads_clear( thread3 );
    Threads_delete( thread3 );
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

    SUITE_ADD_TEST( suite, Test_MTList_lifecycle );
    SUITE_ADD_TEST( suite, Test_MTList_main );
    SUITE_ADD_TEST( suite, Test_MTQueue );
//     SUITE_ADD_TEST( suite, Test_MTMessageQueue );
    SUITE_ADD_TEST( suite, Test_PQueue );
    SUITE_ADD_TEST( suite, Test_PQueueArray );

    CuSuiteRun( suite );
    CuSuiteSummary( suite, output );
    CuSuiteDetails( suite, output );

    Any_fprintf( stderr, "%s\n", output->buffer );

    CuSuiteDelete( suite );
    CuStringDelete( output );

    return suite->failCount;
}


/* EOF */
