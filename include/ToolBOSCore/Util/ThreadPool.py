#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Run multiple threads at once
#
#  Copyright (c) Honda Research Institute Europe GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

import threading

from ToolBOSCore.Util import Any


class ThreadPool( object ):
    """
        Class for creating and handling a group of threads.
        It is meant to simplify usage of multiple threads at once and reduce
        off-topic code.

        Py3k
        Python3 offers the same functionality with the
        concurrent.futures package and its subclass ThreadPoolExecutor.
    """

    def __init__( self ):
        """
            Creates a new ThreadPool instance.
        """
        self._threads = set()


    def add( self, task, *args, **kwargs ):
        """
            Add new tasks as threads to the ThreadPool.
        """
        Any.requireIsCallable( task )

        _thread = threading.Thread( target=task, args=args, kwargs=kwargs )
        self._threads.add( _thread )


    def run( self ):
        """
            Starts all threads of the ThreadPool and joins them afterwards,
            meaning this function will run until all threads are finished.
        """
        for thread in self._threads:
            thread.start()

        for thread in self._threads:
            thread.join()


# EOF
