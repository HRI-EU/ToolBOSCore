/*
 *  ${packageName}.h
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


#ifndef ${PACKAGENAME}_H
#define ${PACKAGENAME}_H


/*!
 * \mainpage
 *
 * ...documentation goes here...
 */


#include <Any.h>


#if defined(__cplusplus)
extern "C" {
#endif


typedef struct ${packageName}
{
    unsigned long valid;
}
${packageName};


/*!
 * \brief Constructor
 *
 * Do not forget to call the corresponding ${packageName}_delete().
 *
 * \return Returns a new ${packageName} instance or NULL in case of error
 */
${packageName}* ${packageName}_new( void );


/*!
 * \brief Initialize an instance (allocate and set members)
 *
 * Do not forget to call the corresponding ${packageName}_clear().
 *
 * \param self Pointer to a ${packageName} instance
 *
 * \return Returns zero if the object is initialized correctly,
 *         negative error code otherwise
 */
int ${packageName}_init( ${packageName} *self );


/*!
 * \brief Clear an instance
 *
 * \param self Pointer to a ${packageName} instance
 */
void ${packageName}_clear( ${packageName} *self );


/*!
 * \brief Destructor
 *
 * \param self Pointer to a ${packageName} instance
 */
void ${packageName}_delete( ${packageName} *self );


#if defined(__cplusplus)
}
#endif


#endif


/* EOF */
