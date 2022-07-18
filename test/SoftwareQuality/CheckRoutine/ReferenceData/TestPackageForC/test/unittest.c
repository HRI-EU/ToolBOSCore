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

/*--------------------------------------------------------------------------*/
/* Includes                                                                 */
/*--------------------------------------------------------------------------*/


#include <stdlib.h>
#include <Any.h>
#include <TestPackageForC.h>
#include <CuTest.h>


/*--------------------------------------------------------------------------*/
/* HowTo                                                                    */
/*--------------------------------------------------------------------------*/
//
//  1.  Write testcase functions
//      (see examples below)
//
//  2.  List each testcase in main() function
//
//  3.  Compile package and run test program like:
//      $ RunFromSourceTree.sh ./test/\${MAKEFILE_PLATFORM}/unittest
//
//
//----------------------------------------------------------------------------
//
//
//  Assertions provided by CuTest:
//
//      CuFail( testcase, msg );
//      CuAssert( testcase, msg, cond );
//      CuAssertTrue( testcase, cond );
//
//      CuAssertStrEquals( testcase, expected, actual );
//      CuAssertStrEquals_Msg( testcase, msg, expected, actual );
//      CuAssertIntEquals( testcase, expected, actual );
//      CuAssertIntEquals_Msg( testcase, msg, expected, actual );
//      CuAssertDblEquals( testcase, expected, actual, maxDelta );
//      CuAssertDblEquals_Msg( testcase, msg, expected, actual, maxDelta );
//      CuAssertPtrEquals( testcase, expected, actual );
//      CuAssertPtrEquals_Msg( testcase, msg, expected, actual );
//
//      CuAssertPtrNotNull( testcase, ptr );
//      CuAssertPtrNotNullMsg( testcase, msg, ptr );


/*--------------------------------------------------------------------------*/
/* Testcases                                                                */
/*--------------------------------------------------------------------------*/


void Unittest_lifecycle( CuTest *testcase )
{
    TestPackageForC *data = (TestPackageForC*)NULL;

    data = TestPackageForC_new();
    CuAssertTrue( testcase, data != (TestPackageForC*)NULL );

    /* PLEASE ADAPT:

    TestPackageForC_init( data, 123 );
    CuAssertIntEquals( testcase, 123, TestPackageForC_getXY( data ) );

    TestPackageForC_clear( data );

    CuAssertIntEquals( testcase, 0, TestPackageForC_getLength( data ) );
    CuAssertPtrEquals( testcase, 0, data->buffer );
    */

    TestPackageForC_delete( data );
}


void Unittest_toString( CuTest *testcase )
{
    /* EXAMPLE FUNCTION, PLEASE ADAPT */
    ANY_LOG( 0, "Hello, World!", ANY_LOG_INFO );
}


void Unittest_getXY( CuTest *testcase )
{
    /* EXAMPLE FUNCTION, PLEASE ADAPT */
    ANY_LOG( 0, "Hello, World!", ANY_LOG_INFO );
}


/*--------------------------------------------------------------------------*/
/* Boilerplate main function                                                */
/*--------------------------------------------------------------------------*/


int main( int argc, char* argv[] )
{
    CuSuite  *suite  = CuSuiteNew();
    CuString *output = CuStringNew();

    /* TODO: list each testcase here */
    SUITE_ADD_TEST( suite, Unittest_lifecycle );
    SUITE_ADD_TEST( suite, Unittest_toString );
    SUITE_ADD_TEST( suite, Unittest_getXY );

    CuSuiteRun( suite );
    CuSuiteSummary( suite, output );
    CuSuiteDetails( suite, output );
    fprintf( stderr, "%s\n", output->buffer );

    CuStringDelete( output );
    CuSuiteDelete( suite );

    return EXIT_SUCCESS;
}


/* EOF */
