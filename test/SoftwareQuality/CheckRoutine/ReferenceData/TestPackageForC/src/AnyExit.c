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


#include <stdlib.h>

#include <AnyExit.h>
#include <Traps.h>


/* exit callback */
static AnyExitCallBack *_AnyExit_callBack;

/* exit callback pointer to instance */
static void *_AnyExit_callBackInstance;

/* exit callback pointer to user data */
static void *_AnyExit_callBackUserData;

/* flag for AnyExit_exit() to dump call backtrace, default enabled */
static int _AnyExit_dumpStacktrace = 1;


void AnyExit_setCallBack( AnyExitCallBack *callBack, void *instance, void *userData )
{
    _AnyExit_callBack = callBack;
    _AnyExit_callBackInstance = instance;
    _AnyExit_callBackUserData = userData;
}

void AnyExit_getCallBack( AnyExitCallBack **callBack, void **instance, void **userData )
{
    *callBack = _AnyExit_callBack;
    *instance = _AnyExit_callBackInstance;
    *userData = _AnyExit_callBackUserData;
}

int AnyExit_isSet( void )
{
    return _AnyExit_callBack != NULL;
}

void AnyExit_exit( int status )
{
    /* dump the call backtrace only if defined and status < 0 */
    if ( _AnyExit_dumpStacktrace && status < 0 )
    {
        Traps_callTrace();
    }

    if ( _AnyExit_callBack )
    {
        ANY_LOG( 1, "AnyExit callbacks are disabled for safety reasons, using normal exit() instead", ANY_LOG_INFO );
        /* Call the user's callback */
        /* _AnyExit_callBack( _AnyExit_callBackInstance, status, _AnyExit_callBackUserData ); */
        /* return; */
    }

    /* call normal exit() if not defined user's exit callback */
    exit( status );
}

void AnyExit_setDumpBacktrace( int status )
{
    _AnyExit_dumpStacktrace = status;
}

int AnyExit_getDumpBacktrace( void )
{
    return _AnyExit_dumpStacktrace;
}

/* EOF */
