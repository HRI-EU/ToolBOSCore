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


#ifndef BASE_TYPES_H
#define BASE_TYPES_H


#ifdef __cplusplus
extern "C" {
#endif


/*--------------------------------------------------------------------------*/
/* Include files                                                            */
/*--------------------------------------------------------------------------*/


#include <inttypes.h>
#include <stdint.h>


/*--------------------------------------------------------------------------*/
/* Portable datatypes                                                       */
/*--------------------------------------------------------------------------*/


/*!
 * \brief BaseBool type (int wrapper)
 */
typedef signed int BaseBool;

/*!
 * \brief BaseI8 type for 8 bit signed integer number
 */
typedef int8_t BaseI8;

/*!
 * \brief BaseUI8 type for 8 bit unsigned integer number
 */
typedef uint8_t BaseUI8;

/*!
 * \brief BaseI16 type for 16 bit signed integer number
 */
typedef int16_t BaseI16;

/*!
 * \brief BaseUI16 type for 16 bit unsigned integer number
 */
typedef uint16_t BaseUI16;

/*!
 * \brief BaseI32 type for 32 bit signed integer number
 */
typedef signed int BaseI32;

/*!
 * \brief BaseUI32 type for 32 bit unsigned integer number
 */
typedef unsigned int BaseUI32;

/*!
 * \brief BaseF32 type for 32 bit float number
 */
typedef float BaseF32;

/*!
 * \brief BaseF64 type for 64 bit float number
 */
typedef double BaseF64;

/*!
 * \brief BaseI64 type for 64 bit signed long number
 */
typedef int64_t BaseI64;

/*!
 * \brief BaseUI64 type for 64 bit unsigned long number
 */
typedef uint64_t BaseUI64;

/*!
 * \brief BaseChar type (for consistent Base* usage)
 *
 * This is a fixed mapping to 'char' and added for consistency reasons
 * (to not sometimes use \c BaseI8 and sometimes plain \c char).
 */
typedef char BaseChar;

/*!
 * \struct BaseC32
 * \brief BaseC32 type for 32 bit complex number
 */
typedef struct BaseC32
{
    BaseF32 real;
    /*!< real part */
    BaseF32 imag;   /*!< imaginary part */
}
        BaseC32;

/*!
 * \struct BaseC64
 * \brief BaseC64 type for 64 bit complex number
 */
typedef struct BaseC64
{
    BaseF64 real;
    /*!< real part */
    BaseF64 imag;   /*!< imaginary part */
}
        BaseC64;


/*--------------------------------------------------------------------------*/
/* Min/Max values (ranges)                                                  */
/*--------------------------------------------------------------------------*/


#define BASEBOOL_MIN     ((BaseBool)0)
#define BASEBOOL_MAX     ((BaseBool)1)

#define BASEI8_MIN       ((BaseI8)INT8_MIN)
#define BASEI8_MAX       ((BaseI8)INT8_MAX)

#define BASEUI8_MIN      ((BaseUI8)0)
#define BASEUI8_MAX      ((BaseUI8)UINT8_MAX)

#define BASEI16_MIN      ((BaseI16)INT16_MIN)
#define BASEI16_MAX      ((BaseI16)INT16_MAX)

#define BASEUI16_MIN     ((BaseUI16)0)
#define BASEUI16_MAX     ((BaseUI16)UINT16_MAX)

#define BASEI32_MIN      ((BaseI32)INT32_MIN)
#define BASEI32_MAX      ((BaseI32)INT32_MAX)

#define BASEUI32_MIN     ((BaseUI32)0)
#define BASEUI32_MAX     ((BaseUI32)UINT32_MAX)

/* float is 2^(-126) .. 2 − 2^(−23) × 2^(127) */
#define BASEF32_MIN      ((BaseF32)-3.402823466e38)
#define BASEF32_MAX      ((BaseF32)3.402823466e38)

#define BASEF64_MIN      ((BaseF64)-1.7e308)
#define BASEF64_MAX      ((BaseF64)1.7e308)

#define BASEI64_MIN      ((BaseI64)INT64_MIN)
#define BASEI64_MAX      ((BaseI64)INT64_MAX)

#define BASEUI64_MIN     ((BaseUI64)0)
#define BASEUI64_MAX     ((BaseUI64)UINT64_MAX)


/*--------------------------------------------------------------------------*/
/* printf() / scanf() format specifiers                                     */
/*--------------------------------------------------------------------------*/


/* actual to be used: */

#define BASEBOOL_PRINT   PRIu32

#define BASEI8_PRINT     PRIi8
#define BASEI16_PRINT    PRIi16
#define BASEI32_PRINT    PRIi32
#define BASEI64_PRINT    PRIi64

#define BASEUI8_PRINT    PRIu8
#define BASEUI16_PRINT   PRIu16
#define BASEUI32_PRINT   PRIu32
#define BASEUI64_PRINT   PRIu64

#define BASEF32_PRINT    "f"
#define BASEF64_PRINT    "f"

#define BASEBOOL_SCAN    SCNu32

#define BASEI8_SCAN      SCNi8
#define BASEI16_SCAN     SCNi16
#define BASEI32_SCAN     SCNi32
#define BASEI64_SCAN     SCNi64

#define BASEUI8_SCAN     SCNu8
#define BASEUI16_SCAN    SCNu16
#define BASEUI32_SCAN    SCNu32
#define BASEUI64_SCAN    SCNu64

#define BASEF32_SCAN     "f"
#define BASEF64_SCAN     "lf"


/* also provide macro for size_t (for convenience) */

#if defined(__32BIT__)

#define SIZE_PRINT       PRIu32
#define SIZE_SCAN        SCNu32

#elif defined(__64BIT__)

#define SIZE_PRINT       PRIu64
#define SIZE_SCAN        SCNu64

#else

#define SIZE_PRINT       "z"
#define SIZE_SCAN        "z"

#endif


/* legacy: */

#define BASEBOOL_FORMAT  BASEBOOL_PRINT

#define BASEI8_FORMAT    BASEI8_PRINT
#define BASEI16_FORMAT   BASEI16_PRINT
#define BASEI32_FORMAT   BASEI32_PRINT
#define BASEI64_FORMAT   BASEI64_PRINT

#define BASEUI8_FORMAT   BASEUI8_PRINT
#define BASEUI16_FORMAT  BASEUI16_PRINT
#define BASEUI32_FORMAT  BASEUI32_PRINT
#define BASEUI64_FORMAT  BASEUI64_PRINT

#define BASEF32_FORMAT   "f"
#define BASEF64_FORMAT   "f"


#ifdef __cplusplus
}
#endif


#endif


/* EOF */
