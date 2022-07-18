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


#ifndef ANYEXIT_H
#define ANYEXIT_H


#if defined(__cplusplus)
extern "C" {
#endif

/* 
 * The prototype of called function is:
 *
 * void callback( void *instance, int status, void *userData )
 *
 */
typedef void (AnyExitCallBack)(void*, int, void*); 

void AnyExit_setCallBack( AnyExitCallBack *callBack, void *instance, void *userData );

void AnyExit_getCallBack( AnyExitCallBack **callBack, void **instance, void **userData );

int AnyExit_isSet( void );

void AnyExit_exit( int status );

void AnyExit_setDumpBacktrace( int status );

int AnyExit_getDumpBacktrace( void );

#if defined(__cplusplus)
}
#endif

#endif /* ANYEXIT_H */

/* EOF */
