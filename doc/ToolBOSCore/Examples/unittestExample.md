## unittest.c         {#unittest}


    /*
     *  unittest.c
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
    /*
     * To get this program compiled include the following in your CMakeLists.txt:
     *
     * bst_find_package(External/cutest/1.5)
     *
     *
     * You can look-up the available assertion macros in the file:
     *
     * ${SIT}/External/cutest/1.5/include/CuTest.h
     */
    /*---------------------------------------------------------------------------*/
    /* Includes                                                                  */
    /*---------------------------------------------------------------------------*/
    #include <stdlib.h>
    #include <Any.h>
    #include <CuTest.h>
    /*---------------------------------------------------------------------------*/
    /* Test cases                                                                */
    /*---------------------------------------------------------------------------*/
    void Test_myFunc1( CuTest *tc )
    {
        /* ... test something ...*/
        CuAssertTrue( tc, 1 + 2 == 3 );
    }
    void Test_myFunc2( CuTest *tc )
    {
        /* ... test something ...*/
        CuAssertIntEquals( tc, 42, 41 );
    }
    /*---------------------------------------------------------------------------*/
    /* Main program                                                              */
    /*---------------------------------------------------------------------------*/
    int main( void )
    {
        CuSuite  *suite   = CuSuiteNew();
        CuString *output  = CuStringNew();
        char     *verbose = (char*)NULL;
        ANY_REQUIRE( suite );
        ANY_REQUIRE( output );
        verbose = getenv( (char*)"VERBOSE" );
        if( verbose != NULL && Any_strcmp( verbose, (char*)"TRUE" ) == 0 )
        {
            Any_setDebugLevel( 10 );
        }
        else
        {
            Any_setDebugLevel( 1 );
        }
        /* TODO: list each function here that shall be executed */
        SUITE_ADD_TEST( suite, Test_myFunc1 );
        SUITE_ADD_TEST( suite, Test_myFunc2 );
        CuSuiteRun( suite );
        CuSuiteSummary( suite, output );
        CuSuiteDetails( suite, output );
        Any_fprintf( stderr, "%s\n", output->buffer );
        CuSuiteDelete( suite );
        CuStringDelete( output );
        return EXIT_SUCCESS;
    }
    /* EOF */
    
