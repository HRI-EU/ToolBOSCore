# -*- coding: utf-8 -*-
#
#  tiny convenience wrapper for Python's optparse class
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


import optparse


#----------------------------------------------------------------------------
# Public class
#----------------------------------------------------------------------------


ARGSMANAGER_PARAM_MANDATORY = ( 'ARGSMANAGER', 'MANDATORY' )


class ArgsManager( object ):
    """
        Processes the input arguments
    """


    def __init__( self, description ):
        """
            Creates a new ArgsManager

            Inputs:
            - description: script description
        """


        class ArgsManagerFormatter( optparse.IndentedHelpFormatter ):
            """
                ArgsManager specific formatter. It avoids the automatic formatting
                of the user specified epilog
            """

            def format_description( self, description ):
                if not description:
                    return ''
                else:
                    return self.parser.expand_prog_name( description )


            def format_epilog( self, epilog ):
                if not epilog:
                    return ''
                else:
                    return self.parser.expand_prog_name( epilog )


        from ToolBOSCore.Settings.ToolBOSSettings import getConfigOption

        try:
            bugtrackURL = getConfigOption( 'bugtrackURL' )
            epilog      = '\nPlease report bugs on JIRA (%s).' % bugtrackURL
        except AttributeError:
            # Unable to retrieve option
            #
            # This happens within ToolBOS-Setup.py: In a brand-new user
            # environment TOOLBOSCORE_ROOT is not defined, yet.
            # Hence we are not able to determine the location of the
            # fallback ToolBOS.conf.
            epilog      = ''

        self._optParser = optparse.OptionParser( formatter = ArgsManagerFormatter() )
        self._mandatoryArgs = []
        self._optionalArgs = []
        self._options = []

        self._description = optparse.IndentedHelpFormatter().format_description( description )
        self._example = ''
        self._epilog = epilog
        self._usage = ''
        self._unhandled = None

        self._areOptions = False


    def setExample( self, example ):
        """
            Sets examples for the considered script

            Inputs:
            - example: examples string
        """
        self._example = example


    def setEpilog( self, epilog ):
        """
            Sets the epilog for the considered script

            Inputs:
            - epilog: help menu epilog string
        """
        self._epilog = epilog


    def setUsage( self, usage ):
        """
            Sets the script usage

            Inputs:
            - usage: script usage
        """
        self._usage = usage


    def addOption( self, name, help, flagShort, flagLong = '', default = None, type = None,
                action = 'store', nValues = 1, metaVar = None ):
        """
            Adds a script option description into the ArgsManager

            Inputs:
            - name: option name. It must match the name of the associated function paramenter
            - help: option help message
            - flagShort: short flag. E.g. -f
            - flagLong: long flag. E.g. --file
            - default: option default value
            - type: option type
            - action: one of values:
                * 'store': if the flag required a value.
                * 'store_true': to assign a True value to the flag
                * 'store_false': to assign a False value to the flag
            - nValues: if action is 'store' multiple values can be specified.
                        Number of expected values
            - metaVar: string to be used into the help menu to identify the required value.
                        E.g. Let us suppose to have a '-f' flag that requires the name of
                        a file. In this case the 'metaVar' could be '<FILENAME>'. In the help
                        menu you will see '-f <FILENAME>'
        """
        self._areOptions = True
        metaVar = metaVar if metaVar else name.upper()

        if nValues > 1:
            for x in range( nValues ):
                metaVar += name + str(x) + ' '

        self._optParser.add_option( flagShort, flagLong, default = default, type = type,
                                    action = action, help = help, dest = name, metavar = metaVar )

        self._options.append( name )


    def addArgument( self, name, help, default = None, type = None, metaVar = None, isMultiple = False ):
        """
            Adds a script argument description into the ArgsManager

            Inputs:
            - name: argument name. It must match the name of the associated function paramenter
            - help: argument help message
            - default: argument default value. If the argument is mandatory use the symbol
                        ARGSMANAGER_PARAM_MANDATORY
            - type: argument type
            - metaVar: string to be used into the help menu to identify the required value.
                        E.g. Let us suppose to have a argument to specify a file.
                        In this case the 'metaVar' could be '<FILENAME>'. In the usage menu
                        you will see '<FILENAME>'
            - isMultiple: if multiple value are required

        Note that if the argument required multiple values then no other arguments can follow.
        """
        metaVar = metaVar if metaVar else name.upper()

        try:
            type = eval( type ) if type else lambda x: x
        except:
            raise ValueError( 'Invalid type %s specified' % type )

        if default is ARGSMANAGER_PARAM_MANDATORY:
            self._mandatoryArgs.append( ( name, help, metaVar, isMultiple, type ) )
        else:
            self._optionalArgs.append( ( name, help, metaVar, isMultiple, type, default ) )


    def parseArguments( self, args=None ):
        """
            Parses the input arguments based on the specified options and arguments

            Output:
            Dictonary holding 'option/argument name': 'value'
        """
        self._configure()
        opts, args = self._optParser.parse_args( args=args )

        functionParameterDict = {}
        self._unhandled       = args

        if len( args ) < len( self._mandatoryArgs ):
            self._optParser.error( 'Required arguments are missing, please ' + \
                                   'see the help page for details.' )

        for mandatory in self._mandatoryArgs:
            type = mandatory[ 4 ]

            if mandatory[ 3 ]:
                functionParameterDict[ mandatory[ 0 ] ] = [ type( arg ) for arg in args ]
                args = []
            else:
                functionParameterDict[ mandatory[ 0 ] ] = type( args[ 0 ] )
                del args[ 0 ]

        for optional in self._optionalArgs:
            type = optional[ 4 ]

            if optional[ 3 ]:
                functionParameterDict[ optional[ 0 ] ] = [ type( arg ) for arg in args ]
                args = []
            else:
                if len( args ) > 0:
                    functionParameterDict[ optional[ 0 ] ] = type( args[ 0 ] )
                    del args[ 0 ]
                else:
                    functionParameterDict[ optional[ 0 ] ] = optional[ 5 ]

        for optName in self._options:
            functionParameterDict[ optName ] = getattr( opts, optName )

        return functionParameterDict


    def _configure( self ):
        """
            Configures properly the ArgsManager before the parsing of the input arguments
        """
        for index in range( len( self._mandatoryArgs ) ):
            if self._mandatoryArgs[ index ][ 3 ] and ( ( index != len( self._mandatoryArgs ) - 1 ) or self._optionalArgs ):
                    self._optParser.error( 'No other arguments after an multiple value argument can be specified. ' +
                                           'Please check the type and the order of the arguments' )

        #Checking optional arguments
        for index in range( len( self._optionalArgs ) ):
            if self._optionalArgs[ index ][ 3 ] and ( index != len( self._optionalArgs ) - 1 ):
                self._optParser.error( 'No other arguments after an multiple value argument can be specified. ' +
                                       'Please check the type and the order of the arguments' )

        self._optParser.set_usage( self._createUsage() )
        self._optParser.set_description( self._createDescription() )
        self._optParser.epilog = self._createEpilog()


    def _createDescription( self ):
        """
            Generates the final OptParser description taking into account the given
            arguments

            Output:
            Description string
        """
        argumentsDescription = ''

        if self._mandatoryArgs or self._optionalArgs:
            argumentsDescription += "\nArguments:\n"

        for arg in self._mandatoryArgs:
            argumentsDescription += '  %s\t\t%s\n' % ( arg[ 2 ], arg[ 1 ] )
        for arg in self._optionalArgs:
            argumentsDescription += '  %s\t\t%s\n' % ( arg[ 2 ], arg[ 1 ] )

        return self._description + argumentsDescription


    def _createEpilog( self ):
        example = ''
        if self._example:
            example = 'Examples:\n%s\n' % self._example

        epilog = ''
        if self._epilog:
            epilog = '%s\n' % self._epilog

        return '\n' + example + epilog + '\n'


    def _createUsage( self ):
        """
            Generates the usage string if it was not specified by the user

            Output:
            Usage string
        """
        if self._usage:
            return self._usage

        options = '<OPTIONS>' if self._areOptions else ''

        if self._mandatoryArgs:
            mandatoryArgsUsage = self._makeUsageForArguments( self._mandatoryArgs )
        else:
            mandatoryArgsUsage = ''

        if self._optionalArgs:
            optionalArgsUsage = self._makeUsageForArguments( self._optionalArgs, '[', ']' )
        else:
            optionalArgsUsage = ''

        return '%prog ' + '%s %s %s' % ( options, mandatoryArgsUsage.strip(), optionalArgsUsage.strip() )


    def _makeUsageForArguments( self, argumentsList, prefix = '', postfix = '' ):
        """
            Generates the usage string for the options or the arguments

            Inputs:
            - argumentsList: list of tuples describing arguments/options
            - prefix: prefix charater
            - postfix: postfix character

            Output:
            Usage string related with the options/arguments
        """
        usage = ''
        for arg in argumentsList:
            if arg[ 3 ]:
                usage += '%s<%s_0 ... %s_N>%s ' % ( prefix, arg[ 2 ], arg[ 2 ], postfix )
                break
            else:
                usage += '%s<%s>%s ' % ( prefix, arg[ 2 ], postfix )

        return usage


    def getUnhandledArguments( self ):
        """
            Returns the list of unhandled arguments, f.i. parameters which
            are not matching any of the script's commandline options.
        """
        return self._unhandled


# EOF
