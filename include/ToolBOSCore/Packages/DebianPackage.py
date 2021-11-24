# -*- coding: utf-8 -*-
#
#  Model for Debian/Ubuntu packages
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


import subprocess

from ToolBOSCore.Packages                 import ProjectProperties

from ToolBOSCore.Platforms                import Debian
from ToolBOSCore.Packages.AbstractPackage import AbstractPackage


class DebianPackage( AbstractPackage ) :
    """
        Representative for a *.deb package found on Debian/Ubuntu etc.
        Linux systems.
    """
    def __init__( self, url ):
        super( DebianPackage, self ).__init__( url )

        self._isInstalled = None
        self.name        = ProjectProperties.splitURL( url )[1]
        self.url         = url


    def isInstalled( self ):
        return Debian.isInstalled( self.name )


    def retrieveDependencies( self ):
        # Debian packages are known to lead to cyclic dependencies,
        # e.g.:
        #
        # gcc-4.9-base --> libc6 --> libgcc1 --> gcc-4.9-base
        #
        # Skipping recursive dependency resolution because an
        # installed Debian package implies that its dependencies
        # are present (unless sth. is really broken).

        try:
            self._isInstalled = Debian.isInstalled( self.name )
            self.depSet      = set()
            self.depTree     = list()
        except subprocess.CalledProcessError:
            self._isInstalled = False
            raise EnvironmentError( '%s: Not installed on this system' % self.name )


# EOF
