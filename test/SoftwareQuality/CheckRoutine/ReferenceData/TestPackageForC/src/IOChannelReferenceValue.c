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


#include <IOChannel.h>
#include <IOChannelReferenceValue.h>


typedef enum
{
    Int,
    UInt,
    Long,
    ULong
} IOChannelReferenceValueAllowedType;

typedef enum
{
    decimal,
    exadecimal,
    octal
} IOChannelReferenceValueNotationType;

typedef struct IOChannelAccessMode
{
    char *name;
    IOChannelMode value;
} IOChannelAccessMode;

typedef struct IOChannelAccessPermission
{
    char *name;
    IOChannelPermissions value;
} IOChannelAccessPermission;


static void IOChannelReferenceValue_getNumber( IOChannelReferenceValue **vect,
                                               char *reference,
                                               IOChannelReferenceValueAllowedType type,
                                               void *result );

static void IOChannelReferenceValue_stringToNumber( char *value,
                                                    IOChannelReferenceValueAllowedType type,
                                                    void *result );


void IOChannelReferenceValue_listItemSet( IOChannelReferenceValue **headList,
                                          char *reference,
                                          char *value )
{
    IOChannelReferenceValue *newItem = (IOChannelReferenceValue *)NULL;
    IOChannelReferenceValue *currentPtr = (IOChannelReferenceValue *)NULL;

    ANY_REQUIRE( headList );
    ANY_REQUIRE( reference );
    ANY_REQUIRE( value );

    currentPtr = *headList;

    while( currentPtr != NULL )
    {
        if( Any_strcmp( currentPtr->reference, reference ) == 0 )
        {
            ANY_FREE( currentPtr->value );
            currentPtr->value = value;
            return;
        }

        if( currentPtr->next == NULL )
        {
            break;
        }

        currentPtr = currentPtr->next;
    }

    newItem = ANY_TALLOC( IOChannelReferenceValue );
    ANY_REQUIRE_MSG( newItem, "Cannot allocate memory for new item." );

    newItem->reference = reference;
    newItem->value = value;
    newItem->next = NULL;

    if( currentPtr != NULL )
    {
        currentPtr->next = newItem;
    }
    else
    {
        *headList = newItem;
    }
}


int IOChannelReferenceValue_listToVector( IOChannelReferenceValue *headList,
                                          IOChannelReferenceValue ***vector )
{
    int vectDim = 0;
    int i = 0;
    IOChannelReferenceValue *currentPtr = (IOChannelReferenceValue *)NULL;

    ANY_REQUIRE( headList );
    ANY_REQUIRE( vector );

    currentPtr = headList;

    while( headList != NULL )
    {
        vectDim++;
        headList = headList->next;
    }

    headList = currentPtr;

    if( vectDim > 0 )
    {
        *vector = ANY_NTALLOC( vectDim + 1, IOChannelReferenceValue * );
        ANY_REQUIRE( *vector );
        currentPtr = headList;

        while( currentPtr != NULL )
        {
            *( *vector + i ) = currentPtr;
            i++;
            currentPtr = currentPtr->next;
        }
        *( *vector + vectDim ) = NULL;
    }

    return ( vectDim );
}


int IOChannelReferenceValue_parseReferenceValue( const char *openString,
                                                 IOChannelReferenceValue ***vector )
{
    int counter = 0;
    char *referenceBuffer = (char *)NULL;
    char *referenceValue = (char *)NULL;
    const char *tmp = (char *)NULL;
    IOChannelReferenceValue *list = (IOChannelReferenceValue *)NULL;
    IOChannelReferenceValue *currentPtr = (IOChannelReferenceValue *)NULL;

    ANY_REQUIRE( openString );
    ANY_REQUIRE( vector );

    while( *openString != IOCHANNELREFERENCEVALUE_EOF )
    {
        IOCHANNELREFERENCEVALUE_SKIPSPACES( openString );

        if( *openString == IOCHANNELREFERENCEVALUE_EOF )
        {
            break;
        }

        if( !IOCHANNELREFERENCEVALUE_ISADMITTEDREFERENCE( *openString ))
        {
            ANY_LOG( 5, "Probable error in string format."
                             "\nFound unadmitted '%c' character.",
                     ANY_LOG_WARNING, *openString );
            goto outLabel;
        }
        else
        {
            IOCHANNELREFERENCEVALUE_GETTOKEN( openString,
                                              referenceBuffer,
                                              IOCHANNELREFERENCEVALUE_ISADMITTEDREFERENCE );

            IOCHANNELREFERENCEVALUE_SKIPSPACES( openString );

            if( *openString != '=' )
            {
                ANY_LOG( 0, "Probable error in openString format."
                                 "\nExpected '=', found '%c'.",
                         ANY_LOG_WARNING, *openString );
                goto outLabel2;
            }
            else
            {
                openString++;
            }

            IOCHANNELREFERENCEVALUE_SKIPSPACES( openString );

            if( *openString == IOCHANNELREFERENCEVALUE_EOF )
            {
                ANY_LOG( 0, "Invalid reference at ", ANY_LOG_ERROR );
                goto outLabel2;
            }

            if( *openString == '\'' )
            {
                tmp = ++openString;
                while( *openString != IOCHANNELREFERENCEVALUE_EOF && *openString != '\'' )
                {
                    openString++;
                }

                if( *openString != '\'' )
                {
                    ANY_LOG( 5, "Expected \"'\" but never found. Reference \"%s\".",
                             ANY_LOG_WARNING, referenceBuffer );
                    goto outLabel2;
                }
                else
                {
                    IOCHANNELREFERENCEVALUE_EXTRACTTOKEN( referenceValue,
                                                          tmp,
                                                          ( openString - tmp ));
                    openString++;
                }
            }
            else if( *openString != IOCHANNELREFERENCEVALUE_EOF )
            {
                IOCHANNELREFERENCEVALUE_GETTOKEN( openString,
                                                  referenceValue,
                                                  IOCHANNELREFERENCEVALUE_ISADMITTEDVALUE );
            }

            if(( referenceBuffer != NULL ) && ( referenceValue != NULL ))
            {
                IOChannelReferenceValue_listItemSet( &list, referenceBuffer, referenceValue );
            }
            else
            {
                ANY_LOG( 0, "Unable to allocate memory for reference at", ANY_LOG_ERROR );
                goto outLabel3;
            }
        }
    }

    ANY_REQUIRE( list );

    counter = IOChannelReferenceValue_listToVector( list, vector );
    ANY_REQUIRE( vector );

    if( counter <= 0 )
    {
        goto outLabel3;
    }
    else
    {
        goto outLabel;
    }

    outLabel3:;

    // free all list
    ANY_REQUIRE( list );
    while( list->next != NULL )
    {
        currentPtr = list;

        ANY_FREE( currentPtr->reference );
        ANY_FREE( currentPtr->value );
        ANY_FREE( currentPtr );

        list = list->next;
    }
    ANY_FREE( list->reference );
    ANY_FREE( list->value );
    ANY_FREE( list );


    outLabel2:;
    if( referenceBuffer != NULL )
    {
        ANY_FREE( referenceBuffer );
    }
    if( referenceValue != NULL )
    {
        ANY_FREE( referenceValue );
    }

    outLabel:;
    return ( counter );
}


char *IOChannelReferenceValue_getString( IOChannelReferenceValue **vect,
                                         char *reference )
{
    char *value = (char *)NULL;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOCHANNELREFERENCEVALUE_GETVALUE( value, vect, reference );

    return ( value );
}


void *IOChannelReferenceValue_getPtr( IOChannelReferenceValue **vect,
                                      char *reference )
{
    char *value = (char *)NULL;
    void *result = (void *)NULL;
    int correct = EOF;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOCHANNELREFERENCEVALUE_GETVALUE( value, vect, reference );

    if( value == NULL )
    {
        goto outLabel;
    }

    correct = Any_sscanf( value, "%p", &result );

    if( correct < 0 )
    {
        result = (void *)NULL;
    }

    outLabel:;
    return ( result );
}


int IOChannelReferenceValue_getInt( IOChannelReferenceValue **vect,
                                    char *reference )
{
    int result = 0;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOChannelReferenceValue_getNumber( vect, reference, Int, &result );

    return ( result );
}


unsigned int IOChannelReferenceValue_getUInt( IOChannelReferenceValue **vect,
                                              char *reference )
{
    unsigned int result = 0;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOChannelReferenceValue_getNumber( vect, reference, UInt, &result );

    return ( result );
}


long int IOChannelReferenceValue_getLong( IOChannelReferenceValue **vect,
                                          char *reference )
{
    long int result = 0;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOChannelReferenceValue_getNumber( vect, reference, Long, &result );

    return ( result );
}


unsigned long IOChannelReferenceValue_getULong( IOChannelReferenceValue **vect,
                                                char *reference )
{
    unsigned long result = 0;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOChannelReferenceValue_getNumber( vect, reference, ULong, &result );

    return ( result );
}


IOChannelMode IOChannelReferenceValue_getAccessMode( char *value )
{
    IOChannelMode mode = 0;
    char *buffer = (char *)NULL;
    int i = 0;
    char operator=( char )
    '|';
    char currentOperator = '\0';
    IOChannelMode temp;
    bool flag = false;

    static IOChannelAccessMode IOChannelDefaultAccessMode[] =
            {
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_R_ONLY ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_W_ONLY ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_RW ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_CREAT ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_TRUNC ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_APPEND ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_CLOSE ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_NOTCLOSE ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_MODE_UNDEFINED )
            };

    static int accessDim = sizeof( IOChannelDefaultAccessMode ) /
                           sizeof( IOChannelAccessMode );

    ANY_REQUIRE( value );

    while( *value != IOCHANNELREFERENCEVALUE_EOF )
    {
        IOCHANNELREFERENCEVALUE_SKIPSPACES( value );

        if( *value == IOCHANNELREFERENCEVALUE_EOF )
        {
            break;
        }
        else if( !IOCHANNELREFERENCEVALUE_ISALPHAUPPER( *value ) &&
                 !IOCHANNELREFERENCEVALUE_ISDIGIT( *value ) &&
                 !IOCHANNELREFERENCEVALUE_ISSIGN( *value ))
        {
            ANY_LOG( 5, "Unexpected character '%c' found.", ANY_LOG_ERROR, *value );
            mode = EOF;
            goto exitLabel;
        }

        IOCHANNELREFERENCEVALUE_GETTOKEN( value,
                                          buffer,
                                          IOCHANNELREFERENCEVALUE_ISADMITTED );

        IOCHANNELREFERENCEVALUE_SKIPSPACES( value );
        currentOperator = *value;

        flag = false;
        if( IOCHANNELREFERENCEVALUE_ISALPHAUPPER( *buffer ))
        {
            for( i = 0; i < accessDim; i++ )
            {
                if( Any_strcmp( buffer, ( *( IOChannelDefaultAccessMode + i )).name ) == 0 )
                {
                    flag = true;
                    break;
                }
            }

            if( flag )
            {
                IOCHANNELREFERENCEVALUE_GETACCESSFLAG( mode, operator,( *( IOChannelDefaultAccessMode + i )).value );
                operator=
                currentOperator;
            }
            else
            {
                ANY_LOG( 5, "Error while matching string.\nFound unknown '%s' mode.",
                         ANY_LOG_ERROR, buffer );
                mode = EOF;
                ANY_FREE( buffer );
                goto exitLabel;
            }
        }
        else
        {
            IOChannelReferenceValue_stringToNumber( buffer, Int, &temp );
            IOCHANNELREFERENCEVALUE_GETACCESSFLAG( mode, operator,
            temp );
            operator=
            currentOperator;
        }

        IOCHANNELREFERENCEVALUE_SKIPSPACES( value );

        if( *value != IOCHANNELREFERENCEVALUE_EOF )
        {
            if(( *value == '|' ) || ( *value == '&' ) || ( *value == '^' ))
            {
                value++;

                IOCHANNELREFERENCEVALUE_SKIPSPACES( value );

                if( *value == IOCHANNELREFERENCEVALUE_EOF )
                {
                    ANY_LOG( 5, "Unexpected character '%c' found.", ANY_LOG_ERROR, *( --value ));
                    mode = EOF;
                    ANY_FREE( buffer );
                    goto exitLabel;
                }
            }
            else
            {
                ANY_LOG( 5, "Expected any operator character but never found.", ANY_LOG_ERROR );
                mode = EOF;
                ANY_FREE( buffer );
                goto exitLabel;
            }
        }

        ANY_FREE( buffer );
    }


    exitLabel:;
    return ( mode );
}


IOChannelPermissions IOChannelReferenceValue_getAccessPermissions( char *value )
{
    IOChannelPermissions perm = 0;
    char *buffer = (char *)NULL;
    int i = 0;
    char operator=( char )
    '|';
    char currentOperator = '\0';
    IOChannelPermissions temp;
    bool flag = false;

    static IOChannelAccessPermission IOChannelDefaultAccessPermissions[] =
            {
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_ALL ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_R_G ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_R_O ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_R_U ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_RWX_G ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_RWX_O ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_RWX_U ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_W_G ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_W_O ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_W_U ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_X_G ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_X_O ),
                    IOCHANNELREFERENCEVALUE_CREATEASSOCIATION( IOCHANNEL_PERMISSIONS_X_U )
            };

    static int accessDim = sizeof( IOChannelDefaultAccessPermissions ) /
                           sizeof( IOChannelAccessPermission );

    ANY_REQUIRE( value );

    while( *value != IOCHANNELREFERENCEVALUE_EOF )
    {
        IOCHANNELREFERENCEVALUE_SKIPSPACES( value );

        if( *value == IOCHANNELREFERENCEVALUE_EOF )
        {
            break;
        }
        else if(( IOCHANNELREFERENCEVALUE_ISALPHAUPPER( *value ) == false ) &&
                ( IOCHANNELREFERENCEVALUE_ISDIGIT( *value ) == false ) &&
                ( IOCHANNELREFERENCEVALUE_ISSIGN( *value ) == false ))
        {
            ANY_LOG( 5, "Unexpected character '%c' found.", ANY_LOG_ERROR, *value );
            perm = EOF;
            goto exitLabel;
        }

        IOCHANNELREFERENCEVALUE_GETTOKEN( value,
                                          buffer,
                                          IOCHANNELREFERENCEVALUE_ISADMITTED );

        IOCHANNELREFERENCEVALUE_SKIPSPACES( value );
        currentOperator = *value;

        flag = false;
        if( IOCHANNELREFERENCEVALUE_ISALPHAUPPER( *buffer ))
        {
            for( i = 0; i < accessDim; i++ )
            {
                if( Any_strcmp( buffer, ( *( IOChannelDefaultAccessPermissions + i )).name ) == 0 )
                {
                    flag = true;
                    break;
                }
            }

            if( flag )
            {
                IOCHANNELREFERENCEVALUE_GETACCESSFLAG( perm, operator,
                        ( *( IOChannelDefaultAccessPermissions + i )).value );
                operator=
                currentOperator;
            }
            else
            {
                ANY_LOG( 5, "Error while matching string.\nFound unknow '%s' permission.", ANY_LOG_ERROR, buffer );
                perm = EOF;
                ANY_FREE( buffer );
                goto exitLabel;
            }
        }
        else
        {
            IOChannelReferenceValue_stringToNumber( buffer, Int, &temp );
            IOCHANNELREFERENCEVALUE_GETACCESSFLAG( perm, operator,
            temp );
            operator=
            currentOperator;
        }

        IOCHANNELREFERENCEVALUE_SKIPSPACES( value );

        if( *value != IOCHANNELREFERENCEVALUE_EOF )
        {
            if(( *value == '|' ) || ( *value == '&' ) || ( *value == '^' ))
            {
                value++;

                IOCHANNELREFERENCEVALUE_SKIPSPACES( value );

                if( *value == IOCHANNELREFERENCEVALUE_EOF )
                {
                    ANY_LOG( 5, "Unexpected character '%c' found.", ANY_LOG_ERROR, *( --value ));
                    perm = EOF;
                    ANY_FREE( buffer );
                    goto exitLabel;
                }
            }
            else
            {
                ANY_LOG( 5, "Expected any operator character after '%s' but never found.", ANY_LOG_ERROR, buffer );
                perm = EOF;
                ANY_FREE( buffer );
                goto exitLabel;
            }
        }

        ANY_FREE( buffer );
    }


    exitLabel:;
    return ( perm );
}


static void IOChannelReferenceValue_getNumber( IOChannelReferenceValue **vect,
                                               char *reference,
                                               IOChannelReferenceValueAllowedType type,
                                               void *result )
{
    char *value = (char *)NULL;

    ANY_REQUIRE( vect );
    ANY_REQUIRE( reference );

    IOCHANNELREFERENCEVALUE_GETVALUE( value, vect, reference );

    if( value )
    {
        IOChannelReferenceValue_stringToNumber( value, type, result );
    }
    else
    {
        ANY_LOG( 5, "Reference '%s' not found.", ANY_LOG_INFO, reference );
    }
}


static void IOChannelReferenceValue_stringToNumber( char *value,
                                                    IOChannelReferenceValueAllowedType type,
                                                    void *result )
{
    char *tmp = (char *)NULL;
    int correct = EOF;
    char *pattern = (char *)NULL;
    IOChannelReferenceValueNotationType notation = decimal;

    ANY_REQUIRE( value );

    tmp = value;
    if( IOCHANNELREFERENCEVALUE_ISSIGN( *tmp ))
    {
        switch( type )
        {
            case Int:
            case Long:
                tmp++;
                break;

            case UInt:
            case ULong:
                ANY_LOG( 5, "Error. Found unexpected '%c' character while matching '%s' value."
                                 "\nValue must be unsigned.",
                         ANY_LOG_ERROR, *value, value );
                return;
                break;

            default:
                ANY_LOG( 5, "Error. Invalid type.", ANY_LOG_ERROR );
                return;
                break;
        }
    }

    if( *tmp == '0' )
    {
        if( *( ++tmp ) == 'x' || *tmp == 'X' )
        {
            /* check for correct exadecimal value */
            IOCHANNELREFERENCEVALUE_ISADMITTEDCHARCHECK( ++tmp, IOCHANNELREFERENCEVALUE_ISXDIGIT );
            notation = exadecimal;
        }
        else if( *( --tmp ) == '0' )
        {
            /* check for correct octal value */
            IOCHANNELREFERENCEVALUE_ISADMITTEDCHARCHECK( tmp, IOCHANNELREFERENCEVALUE_ISOCTALDIGIT );
            notation = octal;
        }
    }
    else
    {
        /* check for correct decimal value */
        IOCHANNELREFERENCEVALUE_ISADMITTEDCHARCHECK( tmp, IOCHANNELREFERENCEVALUE_ISDIGIT );
    }

    switch( type )
    {
        case Int:
            pattern = "%i";
            break;

        case UInt:
            switch( notation )
            {
                case decimal:
                    pattern = "%u";
                    break;

                case exadecimal:
                    pattern = "%x";
                    break;

                case octal:
                    pattern = "%o";
                    break;

                default:
                    break;
            }
            break;

        case Long:
            pattern = "%li";
            break;

        case ULong:
            switch( notation )
            {
                case decimal:
                    pattern = "%lu";
                    break;

                case exadecimal:
                    pattern = "%lx";
                    break;

                case octal:
                    pattern = "%lo";
                    break;

                default:
                    break;
            }
            break;

        default:
            ANY_LOG( 5, "Error. Invalid type.", ANY_LOG_ERROR );
            return;
            break;
    }

    correct = Any_sscanf( value, pattern, result );

    if( !correct )
    {
        result = (void *)NULL;
    }

}


void IOChannelReferenceValue_freeReferenceValueVector( IOChannelReferenceValue ***vect )
{
    IOChannelReferenceValue **current = NULL;

    ANY_REQUIRE( vect );

    current = *vect;

    while( *current )
    {
        ANY_FREE(( *current )->reference );
        ANY_FREE(( *current )->value );
        ANY_FREE( *current );

        current++;
    }
    ANY_FREE( *current );

    ANY_FREE( *vect );

}


/* EOF */
