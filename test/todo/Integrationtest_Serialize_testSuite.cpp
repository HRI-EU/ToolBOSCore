/*
 *  Automated testing of Serialize and serialization features.
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


/* main's argc/argv are unused */
#pragma GCC diagnostic ignored "-Wunused-parameter"


#include <DynamicLoader.h>
#include <Serialize.h>
#include <IOChannel.h>
#include <ArgvParser.h>

/***************
 * CPP Defines *
 ***************/
#define TESTSUITE_PARAM_MAXLEN 256

#ifdef _WINDOWS_
#define SHARED_LIBRARY_EXT ".dll"
#else
#define SHARED_LIBRARY_EXT ".so"
#endif

/**************
 * Data types *
 **************/
static ArgvParserOptionDescriptor optionDescriptors[] =
        {
                { 'h', "help",             ARGVPARSER_NO_PARAMETER, NULL,
                        "display this help" },

                { 'l', "library",          ARGVPARSER_PARAMETER_REQUIRED, "library ",
                        "Library to test serialization." },

                { 'i', "init",             ARGVPARSER_PARAMETER_REQUIRED, "libraryInitString ",
                        "initString to initialize library" },

                { 'c', "channel",          ARGVPARSER_PARAMETER_REQUIRED, "channelInitString ",
                        "initString to initialize IOChannel" },

                { 'f', "serialize-format", ARGVPARSER_PARAMETER_REQUIRED, "format",
                        "Serialization format" },

                { 'o', "options",          ARGVPARSER_PARAMETER_REQUIRED, "options",
                        "Serialization options" },

                { 0, NULL, 0,                                       NULL, NULL }
        };

typedef struct testSuite_args
{
    char *library;
    char *libraryInitString;
    char *channelInitString;
    char *format;
    char *opts;
} testSuite_args;

typedef void *(testSuiteNewFunc)( void );

typedef int   (testSuiteInitFromStringFunc)( void *, char * );

typedef void  (testSuiteSerializeFunc)( void *, const char *, Serialize * );

typedef void  (testSuiteClearFunc)( void * );

typedef void  (testSuiteDeleteFunc)( void * );

typedef struct testSuite_functions
{
    testSuiteNewFunc *newFunc;
    /**< Pointer to a _new() function */
    testSuiteInitFromStringFunc *initFromStringFunc;
    /**< Pointer to a _initFromString() function */
    testSuiteSerializeFunc *serializeFunc;
    /**< Pointer to a _serialize() function */
    testSuiteClearFunc *clearFunc;
    /**< Pointer to a _clear() function */
    testSuiteDeleteFunc *deleteFunc;         /**< Pointer to a _delete() function */
} testSuite_functions;

enum
{
    OPT_HELP, /* Index: 0 */
            OPT_LIBRARY, /* Index: 1 */
            OPT_INIT, /* Index: 2 */
            OPT_CHANNEL, /* Index: 3 */
            OPT_FORMAT, /* Index: 4 */
            OPT_OPTIONS                 /* Index: 5 */
};

/**************
 * Prototypes *
 **************/
static int testSuite_parseArgs( ArgvParser argvParser, int argc, char *argv[], testSuite_args args );

static void usage( ArgvParser *argvParser );

static bool testSuite_loadFunctions( DynamicLoader *dl, const char *library, testSuite_functions *functions );


/**********************
 * Private functions  *
 **********************/

static void usage( ArgvParser *argvParser )
{
    ANY_LOG( 0,
             "Usage: ./testSuite -l [library] -i [libraryInitString] -c [channelInitString] -f [format] -o [options]\n",
             ANY_LOG_INFO );

    ANY_LOG( 0, "Valid options:\n", ANY_LOG_INFO );
    ArgvParser_displayOptionHelp( argvParser, 2 );
}


/* Return Values:
 *
 * -1: Failure
 *  0: OK
 *  1: Help was called
 */
static int testSuite_parseArgs( ArgvParser argvParser, int argc, char *argv[], testSuite_args args )
{
    const char *argument = NULL;
    int retVal = 0;

    if( ArgvParser_initAndSetup( &argvParser,
                                 argc,
                                 argv,
                                 optionDescriptors ) != 0 )
    {
        ANY_LOG( 0, "Error while initializing ArgvParser.", ANY_LOG_ERROR );
        return false;
    }

    do
    {
        int optIdx = 0;
        const char *parameter = NULL;

        optIdx = ArgvParser_getCurrentArgument( &argvParser,
                                                NULL,
                                                NULL,
                                                &parameter );

        switch( optIdx )
        {
            case ARGVPARSER_NO_OPTION:
                if( argument == NULL )
                {
                    argument = parameter;
                }
                else
                {
                    ANY_LOG( 0, "Too many arguments: %s\n\n", ANY_LOG_INFO, parameter );
                    usage( &argvParser );
                    retVal = -1;
                }
                break;

            case OPT_HELP:
                usage( &argvParser );
                retVal = 1;
                break;

            case OPT_LIBRARY:
                Any_strncpy( args.library, parameter, TESTSUITE_PARAM_MAXLEN );
                break;

            case OPT_INIT:
                Any_strncpy( args.libraryInitString, parameter, TESTSUITE_PARAM_MAXLEN );
                break;

            case OPT_CHANNEL:
                Any_strncpy( args.channelInitString, parameter, TESTSUITE_PARAM_MAXLEN );
                break;

            case OPT_FORMAT:
                Any_strncpy( args.format, parameter, TESTSUITE_PARAM_MAXLEN );
                break;

            case OPT_OPTIONS:
                Any_strncpy( args.opts, parameter, TESTSUITE_PARAM_MAXLEN );
                break;

            default:
            {
                ANY_LOG( 0, "Unknown argument: %s\n\n", ANY_LOG_ERROR, parameter );
                usage( &argvParser );
                retVal = -1;
            }
                break;
        } // end Switch
    } while( ArgvParser_advance( &argvParser ) && ( retVal != -1 || retVal != 1 ));


    if( ArgvParser_hasErrorOccurred( &argvParser ))
    {
        ANY_LOG( 0, "Error in command line: %s\n\n", ANY_LOG_ERROR,
                 ArgvParser_getErrorMessage( &argvParser ));

        usage( &argvParser );

        retVal = -1;
    }

    return retVal;
}


static bool testSuite_loadFunctions( DynamicLoader *dl, const char *library, testSuite_functions *functions )
{
    bool retVal = false;

    ANY_REQUIRE( dl );

    functions->newFunc = (testSuiteNewFunc *)DynamicLoader_getSymbolByClassAndMethodName( dl, library, "new" );
    if( functions->newFunc == (testSuiteNewFunc *)NULL )
    {
        ANY_LOG( 0, "Unable to retrieve the New function pointer.", ANY_LOG_ERROR );
        return retVal;
    }

    functions->initFromStringFunc = (testSuiteInitFromStringFunc *)DynamicLoader_getSymbolByClassAndMethodName( dl,
                                                                                                                library,
                                                                                                                "initFromString" );
    if( functions->initFromStringFunc == (testSuiteInitFromStringFunc *)NULL )
    {
        ANY_LOG( 0, "Unable to retrieve the initFromString function pointer.", ANY_LOG_ERROR );
        return retVal;
    }

    functions->serializeFunc = (testSuiteSerializeFunc *)DynamicLoader_getSymbolByClassAndMethodName( dl, library,
                                                                                                      "serialize" );
    if( functions->serializeFunc == (testSuiteSerializeFunc *)NULL )
    {
        ANY_LOG( 0, "Unable to retrieve the Serialize function pointer.", ANY_LOG_ERROR );
        return retVal;
    }

    functions->clearFunc = (testSuiteClearFunc *)DynamicLoader_getSymbolByClassAndMethodName( dl, library, "clear" );
    if( functions->clearFunc == (testSuiteClearFunc *)NULL )
    {
        ANY_LOG( 0, "Unable to retrieve the Clear function pointer.", ANY_LOG_ERROR );
        return retVal;
    }

    functions->deleteFunc = (testSuiteDeleteFunc *)DynamicLoader_getSymbolByClassAndMethodName( dl, library, "delete" );
    if( functions->deleteFunc == (testSuiteDeleteFunc *)NULL )
    {
        ANY_LOG( 0, "Unable to retrieve the Delete function pointer.", ANY_LOG_ERROR );
        return retVal;
    }

    retVal = true;
    return retVal;
}


/********
 * Main *
 ********/

int main( int argc, char *argv[] )
{
    ArgvParser argvParser;
    int parseRetVal;
    DynamicLoader *dl = NULL;
    IOChannel *channel = (IOChannel *)NULL;
    Serialize *serializer = (Serialize *)NULL;
    char *libraryToLoad = (char *)NULL;
    testSuite_args args;
    testSuite_functions functions;
    void *typeInstanceWriter = (void *)NULL;
    void *typeInstanceReader = (void *)NULL;
    char *verbose = (char *)NULL;

    verbose = getenv((char *)"VERBOSE" );
    if( verbose != NULL && Any_strcmp( verbose, (char *)"TRUE" ) == 0 )
    {
        Any_setDebugLevel( 10 );
    }
    else
    {
        Any_setDebugLevel( 1 );
    }

    args.library = (char *)ANY_BALLOC( TESTSUITE_PARAM_MAXLEN * sizeof( char ));
    args.libraryInitString = (char *)ANY_BALLOC( TESTSUITE_PARAM_MAXLEN * sizeof( char ));
    args.channelInitString = (char *)ANY_BALLOC( TESTSUITE_PARAM_MAXLEN * sizeof( char ));
    args.format = (char *)ANY_BALLOC( TESTSUITE_PARAM_MAXLEN * sizeof( char ));
    args.opts = (char *)ANY_BALLOC( TESTSUITE_PARAM_MAXLEN * sizeof( char ));

    libraryToLoad = (char *)ANY_BALLOC( TESTSUITE_PARAM_MAXLEN * sizeof( char ));

    ANY_REQUIRE( args.library );
    ANY_REQUIRE( args.libraryInitString );
    ANY_REQUIRE( args.channelInitString );
    ANY_REQUIRE( args.format );
    ANY_REQUIRE( args.opts );
    ANY_REQUIRE( libraryToLoad );

    memset( args.library, 0x00, TESTSUITE_PARAM_MAXLEN );
    memset( args.libraryInitString, 0x00, TESTSUITE_PARAM_MAXLEN );
    memset( args.channelInitString, 0x00, TESTSUITE_PARAM_MAXLEN );
    memset( args.format, 0x00, TESTSUITE_PARAM_MAXLEN );
    memset( args.opts, 0x00, TESTSUITE_PARAM_MAXLEN );


    /************************
     * Parsing of arguments *
     ************************/
    parseRetVal = testSuite_parseArgs( argvParser, argc, argv, args );


    /* ensure strings are properly null-terminated after _parseArgs() */
    args.library[ TESTSUITE_PARAM_MAXLEN - 1 ] = '\0';
    args.libraryInitString[ TESTSUITE_PARAM_MAXLEN - 1 ] = '\0';
    args.channelInitString[ TESTSUITE_PARAM_MAXLEN - 1 ] = '\0';
    args.format[ TESTSUITE_PARAM_MAXLEN - 1 ] = '\0';
    args.opts[ TESTSUITE_PARAM_MAXLEN - 1 ] = '\0';


    if( parseRetVal == -1 )
    {
        ANY_LOG( 0, "An error occurred while parsing arguments from command line.", ANY_LOG_INFO );
        goto exitLabel;
    }
    else if( parseRetVal == 1 )
    {
        goto exitLabel;
    }

    ANY_REQUIRE_MSG( Any_strlen( args.library ) > 0, "You need to specify which library to load." );
    ANY_REQUIRE_MSG( Any_strlen( args.channelInitString ) > 0, "You need to specify the IOChannel initString." );
    ANY_REQUIRE_MSG( Any_strlen( args.format ) > 0, "You need to specify the Serialize format." );

    /*******************
     * Initializations *
     *******************/
    /* IOChannel */
    channel = IOChannel_new();
    ANY_REQUIRE( channel );
    IOChannel_init( channel );
    if( !IOChannel_openFromString( channel, args.channelInitString ))
    {
        ANY_LOG( 0, "Unable to open IOChannel", ANY_LOG_ERROR );
        goto clearLabel;
    }

    /* Serialize */
    serializer = Serialize_new();
    ANY_REQUIRE( serializer );
    Serialize_init( serializer, channel, SERIALIZE_STREAMMODE_NORMAL );
    Serialize_setMode( serializer, SERIALIZE_MODE_WRITE );
    Serialize_setFormat( serializer, args.format, args.opts );

    /* Dynamic Loader */
    dl = DynamicLoader_new();
    ANY_REQUIRE_MSG( dl, "Unable to allocate memory for a new DynamicLoader instance" );

    /* Get requested library and its symbols */
    Any_snprintf( libraryToLoad, TESTSUITE_PARAM_MAXLEN, "lib%s"
            SHARED_LIBRARY_EXT, args.library );
    if( DynamicLoader_init( dl, libraryToLoad ) != 0 )
    {
        ANY_LOG( 0, "Error loading library %s: %s", ANY_LOG_ERROR, args.library, DynamicLoader_getError( dl ));
        goto clearLabel;
    }

    if( !testSuite_loadFunctions( dl, args.library, &functions ))
    {
        ANY_LOG( 0, "Error loading functions.", ANY_LOG_ERROR );
        goto clearLabel;
    }

    /* Create object and serialize it to stream */

    typeInstanceWriter = functions.newFunc();
    ANY_REQUIRE( typeInstanceWriter );

    functions.initFromStringFunc( typeInstanceWriter, args.libraryInitString );

    functions.serializeFunc( typeInstanceWriter, "test", serializer );

    functions.clearFunc( typeInstanceWriter );
    functions.deleteFunc( typeInstanceWriter );

    /* Read back what we wrote */

    IOChannel_rewind( channel );
    Serialize_setMode( serializer, SERIALIZE_MODE_READ );

    typeInstanceReader = functions.newFunc();
    ANY_REQUIRE( typeInstanceReader );

    functions.initFromStringFunc( typeInstanceReader, args.libraryInitString );

    functions.serializeFunc( typeInstanceReader, "test", serializer );

    functions.clearFunc( typeInstanceReader );
    functions.deleteFunc( typeInstanceReader );

    /********
     * Exit *
     ********/
    clearLabel:
    DynamicLoader_clear( dl );
    DynamicLoader_delete( dl );

    IOChannel_close( channel );
    IOChannel_clear( channel );
    IOChannel_delete( channel );

    Serialize_clear( serializer );
    Serialize_delete( serializer );

    exitLabel:

    ANY_FREE( libraryToLoad );

    ANY_FREE( args.library );
    ANY_FREE( args.libraryInitString );
    ANY_FREE( args.channelInitString );
    ANY_FREE( args.format );
    ANY_FREE( args.opts );

    return EXIT_SUCCESS;
}


/* EOF */
