/*
*  TestPackageForC.h
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


#ifndef TESTPACKAGEFORC_H
#define TESTPACKAGEFORC_H


/*!
 * \mainpage
 *
 * ...documentation goes here...
 */


#include <Any.h>


#if defined(__cplusplus)
extern "C" {
#endif


typedef struct TestPackageForC
{
    unsigned long valid;
}
TestPackageForC;


/*!
 * \brief Constructor
 *
 * Do not forget to call the corresponding TestPackageForC_delete().
 *
 * \return Returns a new TestPackageForC instance or NULL in case of error
 */
TestPackageForC* TestPackageForC_new( void );


/*!
 * \brief Initialize an instance (allocate and set members)
 *
 * Do not forget to call the corresponding TestPackageForC_clear().
 *
 * \param self Pointer to a TestPackageForC instance
 *
 * \return Returns zero if the object is initialized correctly,
 *         negative error code otherwise
 */
int TestPackageForC_init( TestPackageForC *self );


/*!
 * \brief Clear an instance
 *
 * \param self Pointer to a TestPackageForC instance
 */
void TestPackageForC_clear( TestPackageForC *self );


/*!
 * \brief Destructor
 *
 * \param self Pointer to a TestPackageForC instance
 */
void TestPackageForC_delete( TestPackageForC *self );


#if defined(__cplusplus)
}
#endif


#endif


/* EOF */
