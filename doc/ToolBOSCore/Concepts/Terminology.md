## Terminology
This page explains various terminologies used throughout the ToolBOSCore toolchain.


### SIT root path

  - main directory of the root SIT (main installation), e.g.:

    * `/hri/sit/latest`


### SIT proxy path

  - main directory of the user's proxy SIT, e.g.:

    * `/home/username/.HRI/sit/latest`


### SIT path

  - location of an unspecific SIT (if it does not matter if
    a proxy or the root SIT is taken), e.g.:

    * `/hri/sit/latest'
    * `/hri/sit/builds/<timestamp>`
    * `/home/username/.HRI/sit/latest`


### Canonical path

  - A software package can be specified / identified by its relative location
    within the *Software Installation Tree (SIT)*.

  - For example, the ToolBOSCore package can be found at
    `/hri/sit/latest/DevelopmentTools/ToolBOSCore/4.3`.
  - The first part `/hri/sit/latest` (= SIT path) is common for all packages.
    Hence, it is sufficient to shortly say `DevelopmentTools/ToolBOSCore/4.3`
    to clearly reference a certain package.
    This is the *canonical path* of the package.


### Package URL

  - Extended version, also O.S. distribution packages and/or specific SITs
    can be referenced, e.g.:

    * `sit://DevelomentTools/ToolBOSCore/4.3`
    * `deb://binutils`
    * `rpm://gcc'


### Package name

  - only the name-part of a package, e.g.:

    * ToolBOSCore
    * gcc


### Package version

  - major.minor version of package, e.g.: 3.0


### Package full version


  - full allowed version string (see install conventions), e.g.:

    * 3.0
    * 3.0.42
    * 3.0.42-experimental


### Package category

  - installation subdirectory (category), e.g.:

    * Libraries
    * Modules/BBCM/InputOutput


### Package path

  - absolute path to a package within a specific SIT, e.g.:

    * `/hri/sit/latest/DevelopmentTools/ToolBOSCore/4.3`

