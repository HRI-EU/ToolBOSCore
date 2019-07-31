/*
 *  HelloWorld.h
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


#ifndef HELLOWORLD_H
#define HELLOWORLD_H


/*!
 * \mainpage
 *
 * ...documentation goes here...
 */


/*--------------------------------------------------------------------------*/
/* Includes                                                                 */
/*--------------------------------------------------------------------------*/


#include <Any.h>


/*--------------------------------------------------------------------------*/
/* Public definitions and datatypes                                         */
/*--------------------------------------------------------------------------*/


ANY_BEGIN_C_DECLS


typedef struct HelloWorld
{
    unsigned long valid;
}
HelloWorld;


/*--------------------------------------------------------------------------*/
/* Public functions                                                         */
/*--------------------------------------------------------------------------*/


HelloWorld* HelloWorld_new( void );

int HelloWorld_init( HelloWorld *self );

// optional:
// int HelloWorld_setup( HelloWorld *self );

void HelloWorld_clear( HelloWorld *self );

void HelloWorld_delete( HelloWorld *self );


ANY_END_C_DECLS


#endif


/* EOF */
