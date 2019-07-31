#
#  Collector header for CMake support files
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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


# use new-style policy scoping
cmake_policy(SET CMP0011 NEW)


if(NOT BST_TOP_LEVEL_DIR)
    set(BST_TOP_LEVEL_DIR ${CMAKE_HOME_DIRECTORY})
endif()


include(${CMAKE_CURRENT_LIST_DIR}/BST_PackageNameAndVersion.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/BST_DefaultSettings.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/BST_DependencyInclusion.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/BST_BuildLibraries.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/BST_BuildExecutables.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/BST_BuildJar.cmake)


macro(bst_printvar)

    get_cmake_property(VAR_NAMES VARIABLES)
    foreach (VAR_NAME ${VAR_NAMES})
        message(STATUS "${VAR_NAME}=${${VAR_NAME}}")
    endforeach()

endmacro()


# EOF
