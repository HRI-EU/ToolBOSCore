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


#include <IOChannelGenericMem.h>
#include <IOChannelReferenceValue.h>


IOCHANNELINTERFACE_CREATE_PLUGIN( Mem );


static void *IOChannelMem_new( void )
{
    return IOChannelGenericMem_new();
}


static bool IOChannelMem_init( IOChannel *self )
{
    ANY_REQUIRE( self );

    IOChannel_valid( self );

    return IOChannelGenericMem_init( self );
}


static bool IOChannelMem_open( IOChannel *self, char *infoString,
                               IOChannelMode mode,
                               IOChannelPermissions permissions, va_list varArg )
{
    long size = 0;
    bool retVal = false;
    void *ptr = (void *)NULL;
    IOChannelReferenceValue **vect = (IOChannelReferenceValue **)NULL;

    ANY_REQUIRE( self );
    ANY_REQUIRE( infoString );

    IOChannel_valid( self );

    IOCHANNELREFERENCEVALUE_CHECKINFOSTRINGCORRECTNESS( infoString );

    IOCHANNEL_GET_ARGUMENT( ptr, void * , varArg );
    IOCHANNEL_GET_ARGUMENT( size, long, varArg );

    IOCHANNELREFERENCEVALUE_BEGINSET( &vect )

    IOCHANNELREFERENCEVALUE_ADDSET( pointer, "%p", ptr );
    IOCHANNELREFERENCEVALUE_ADDSET( size, "%ld", size );

    IOCHANNELREFERENCEVALUE_ENDSET( &vect );

    retVal = IOChannelMem_openFromString( self, vect );

    IOCHANNELREFERENCEVALUE_FREESET( &vect );

    return retVal;
}


static bool IOChannelMem_openFromString( IOChannel *self,
                                         IOChannelReferenceValue **referenceVector )
{
    long size = 0;
    bool retVal = false;
    void *ptr = (void *)NULL;

    ANY_REQUIRE( self );
    ANY_REQUIRE( referenceVector );

    IOChannel_valid( self );

    if( IOCHANNEL_MODEIS_DEFINED( self->mode ))
    {
        if( IOCHANNEL_MODEIS_APPEND( self->mode ))
        {
            retVal = false;
            IOChannel_setError( self, IOCHANNELERROR_BFLGS );
            goto outLabel;
        }
        else
        {
            /* Getting Memory pointer and size */
            ptr = IOChannelReferenceValue_getPtr( referenceVector, IOCHANNELREFERENCEVALUE_POINTER );
            size = IOChannelReferenceValue_getLong( referenceVector, IOCHANNELREFERENCEVALUE_SIZE );

            if( size <= 0 )
            {
                IOChannel_setError( self, IOCHANNELERROR_BSIZE );
                retVal = false;
                goto outLabel;
            }

            if( ptr == NULL )
            {
                if( IOCHANNEL_MODEIS_CREAT( self->mode ))
                {
                    ptr = (void *)ANY_BALLOC( size );
                    if( ptr == NULL )
                    {
                        ANY_LOG( 5, "Unable to allocate memory block.", ANY_LOG_ERROR );
                        IOChannel_setError( self, IOCHANNELERROR_ENOMEM );
                        retVal = false;
                        goto outLabel;
                    }
                    retVal = true;
                }
                else
                {
                    IOChannel_setError( self, IOCHANNELERROR_BMEMPTR );
                    retVal = false;
                    goto outLabel;
                }
            }
            else
            {
                if( IOCHANNEL_MODEIS_CREAT( self->mode ))
                {
                    ANY_LOG( 5, "IOChannelMem(). Triing to create an "
                            "already allocated memory pointer", ANY_LOG_WARNING );
                    IOChannel_setError( self, IOCHANNELERROR_BMEMPTR );
                    retVal = false;
                    goto outLabel;
                }
            }

            IOChannelGenericMem_setPtr( self, ptr, -1, size, false );
            if( IOCHANNEL_MODEIS_TRUNC( self->mode ))
            {
                Any_memset( ptr, '\0', size );
            }

            retVal = true;
        }

    }
    else
    {
        self->mode = IOCHANNEL_MODE_RW;

        /* Getting Memory pointer and size */
        ptr = IOChannelReferenceValue_getPtr( referenceVector, IOCHANNELREFERENCEVALUE_POINTER );
        size = IOChannelReferenceValue_getLong( referenceVector, IOCHANNELREFERENCEVALUE_SIZE );

        if( size <= 0 )
        {
            IOChannel_setError( self, IOCHANNELERROR_BSIZE );
            retVal = false;
            goto outLabel;
        }

        if( ptr == NULL )
        {
            self->mode = self->mode | IOCHANNEL_MODE_CREAT;
            ptr = (void *)ANY_BALLOC( size );
        }

        IOChannelGenericMem_setPtr( self, ptr, -1, size, false );
        retVal = true;

    }

    outLabel:
    return retVal;
}


static long IOChannelMem_read( IOChannel *self, void *buffer, long size )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE_MSG( buffer, "IOChannelMem_read(). Not valid buffer" );
    /* Size == 0 is filtered at high level: so here cannot be == 0 */
    ANY_REQUIRE_MSG( size > 0,
                     "IOChannelMem_read(). Size must be a positive number" );

    return IOChannelGenericMem_read( self, buffer, size );
}


static long IOChannelMem_write( IOChannel *self, const void *buffer, long size )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE_MSG( buffer, "IOChannelMem_write(). Not valid buffer" );
    /* Size == 0 is filtered at high level: so here cannot be == 0 */
    ANY_REQUIRE_MSG( size > 0,
                     "IOChannelMem_write(). Size must be a positive number" );

    return IOChannelGenericMem_write( self, buffer, size );
}


static long IOChannelMem_flush( IOChannel *self )
{
    ANY_REQUIRE( self );

    return IOChannelGenericMem_flush( self );
}


static long long IOChannelMem_seek( IOChannel *self, long long offset, IOChannelWhence whence )
{
    ANY_REQUIRE( self );

    return IOChannelGenericMem_seek( self, offset, whence );
}


static bool IOChannelMem_close( IOChannel *self )
{
    IOChannelGenericMem *streamPtr = (IOChannelGenericMem *)NULL;

    ANY_REQUIRE( self );

    streamPtr = IOChannel_getStreamPtr( self );
    ANY_REQUIRE( streamPtr );

    if( IOCHANNEL_MODEIS_CLOSE( self->mode ))
    {
        /* Warn: use Efence when debugging, sometimes this free seems */
        /*       that not works, but isn't so ! */
        ANY_FREE( streamPtr->ptr );
    }
    return true;
}


static void *IOChannelMem_getProperty( IOChannel *self, const char *propertyName )
{
    IOChannelGenericMem *streamPtr = (IOChannelGenericMem *)NULL;
    void *retVal = (void *)NULL;

    ANY_REQUIRE( self );

    ANY_REQUIRE( propertyName );

    streamPtr = IOChannel_getStreamPtr( self );
    ANY_REQUIRE( streamPtr );

    IOCHANNELPROPERTY_START
    {
        IOCHANNELPROPERTY_PARSE_BEGIN( MemPointer )
        {
            retVal = streamPtr->ptr;
        }
        IOCHANNELPROPERTY_PARSE_END( MemPointer )
    }
    IOCHANNELPROPERTY_END;


    if( !retVal )
    {
        ANY_LOG( 7, "Property '%s' not set or not defined for this stream",
                 ANY_LOG_WARNING, propertyName );
    }

    return retVal;
}


static bool IOChannelMem_setProperty( IOChannel *self, const char *propertyName,
                                      void *property )
{
    ANY_REQUIRE( self );
    ANY_REQUIRE( propertyName );

    return false;
}


static void IOChannelMem_clear( IOChannel *self )
{
    ANY_REQUIRE( self );

    IOChannelGenericMem_clear( self );
}


static void IOChannelMem_delete( IOChannel *self )
{
    ANY_REQUIRE( self );

    IOChannelGenericMem_delete( self );
}


/* EOF */
