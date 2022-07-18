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


#ifndef ARRAYLIST_H
#define ARRAYLIST_H

#include <Any.h>
#include <Mutex.h>

#if defined(__cplusplus)
extern "C" {
#endif


/*!
 * \page ArrayList_About Array lists
 *
 * ArrayList.h contains a thread-safe array list implementation.
 * It is used as stack or item store (object recycling).
 *
 * \see \ref ArrayList_push()
 * \see \ref ArrayList_pop()
 */


typedef struct _ArrayList
{
    ANY_VALID_DECLARE;
    Mutex *mutex;
    int free;
    /*<< count of free elements */
    int count;
    /*<< count of used elements */
    void **buffer;      /*<< buffer */
} ArrayList;

/*!
 * \brief initializes a new ArrayList instance.
 */
ArrayList *ArrayList_new();

/*!
 * \brief deletes an ArrayList instance.
 * \param self pointer to ArrayListInstance
 */
void ArrayList_delete( ArrayList *self );

/*!
 * \brief initializes an ArrayList instance.
 * \param self pointer to ArrayListInstance
 */
void ArrayList_init( ArrayList *self );

/*!
 * \brief Clears an ArrayList instance.
 *        the items in the list won't be deleted
 * \param self pointer to ArrayListInstance
 */
void ArrayList_clear( ArrayList *self );

/*!
 * \brief returns the length of the ArrayList instance.
 * \param self pointer to ArrayListInstance
 */
int ArrayList_length( ArrayList *self );

/*!
 * \brief Adds a new item to the list
 * \param self pointer to ArrayListInstance
 * \param item to be added
 */
void ArrayList_push( ArrayList *self, void *item );

/*!
 * \brief Returns the last item and removes it from the list
 * \param self pointer to ArrayListInstance
 * \return null if no more items are in the list
 */
void *ArrayList_pop( ArrayList *self );

/*!
 * \brief Removes the given item from the list
 * \param self pointer to ArrayListInstance
 * \param item to be removed
 */
void ArrayList_remove( ArrayList *self, void *item );

/*!
 * \brief Returns the item at the index
 * \param self pointer to ArrayListInstance
 * \param index to be retrieved
 * \return null if index is out of range
 */
void *ArrayList_get( ArrayList *self, int index );

/*!
 * \brief Resets the list (without deleting the anyData pointer)
 * \param self pointer to ArrayListInstance
 */
void ArrayList_reset( ArrayList *self );

#if defined(__cplusplus)
}
#endif

#endif /* END ARRAYLIST_H */
