###  License checks (SQ GEN04)

### How it works

The Software Quality checker GEN04 verifies if each and every source
file has the necessary copyright header / license information.

If no license information are provided, the default HRI-EU header
is assumed.

It supports that different files and sub-directories have different
license information. A typical case is that code under a certain
license makes use of 3rd-party-code licensed under a different
(yet compatible) license.

### Specifying license details

The checker is configured in a way that you define a Python variable
'copyright' within your [pkgInfo.py](../../../examples/pkgInfo.py) .
Depending on its datatype the behavior can be fine-tuned.

a) If 'copyright' is a string, this string must be found in each and
   every file of the project. This simple case is for projects where
   all files are under the same simple license string.

    copyright = 'This file is public domain.'

b) If 'copyright' is a list of strings, then all of those strings
   must be found in each file. This way you can realize a multi-line
   license text that applies to all files.

    copyright = [ 'Copyright (c) Honda Research Institute Europe GmbH',
                'Redistribution and use in source and binary forms, with or without',
                'modification, are permitted provided that the following conditions are',
                'met:',
                [...]
                ]

c) In the most complex case 'copyright' can be a dictionary.
   The dict keys are assumed to be relative paths to some
   files/directories, or parts thereof.

   The dict values can again be single strings or lists of strings,
   as shown above. The three dots in the example are placeholders
   for such license information:

    copyright = { './external': ...,
                './external/LibraryA': ...,
                './include/foo.h': ... }

   The above setting will make the GEN04 checker distinguish 4 cases:

   1. All files within the subdirectory 'external/LibraryA' (and any
      of its subdirectories) have one common license header.

   2. All other files within 'external' share a second license header.

   3. The specific file 'include/foo.h' has yet another license.

   4. All other files that may exist anywhere in the project need to
      have the default HRI-EU copyright header.

#### Example: Setting the whole project to HRI-EU license

No setting is needed, as this is the assumed default.

#### Example: Complete package under GPLv3

    copyright = [ 'Copyright (c) Honda Research Institute Europe GmbH',
                'This file is part of ToolBOSLib.',
                'ToolBOSLib is free software: you can redistribute it and/or modify',
                'it under the terms of the GNU General Public License as published by',
                'the Free Software Foundation, either version 3 of the License, or',
                '(at your option) any later version.',
                'ToolBOSLib is distributed in the hope that it will be useful,',
                'but WITHOUT ANY WARRANTY; without even the implied warranty of',
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the',
                'GNU General Public License for more details.',
                'You should have received a copy of the GNU General Public License',
                'along with ToolBOSLib. If not, see <http://www.gnu.org/licenses/>.' ]

#### Example: Project under HRI-EU license, with one file under BSD 3-clause

    copyright = { './external/foo.h':
                    [ 'Copyright (c) Honda Research Institute Europe GmbH',
                    'Redistribution and use in source and binary forms, with or without',
                    'modification, are permitted provided that the following conditions are',
                    'met:',
                    [...]
                    ] }

