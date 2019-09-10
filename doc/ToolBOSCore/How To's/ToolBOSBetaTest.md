### ToolBOS release rollback or beta-test

You may want to use a specific ToolBOS release version (major.minor.patchlevel, e.g. 2.0.1234) in case of:

* trouble with mainstream version (rollback to previous release)
* beta-testing new features (future version)

Set this in your ~/.bashrc:

    export TOOLBOSCORE_AUTO_VERSION=FALSE
    source /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.2.1234

where "2.0.1234" is the particular version you are interested in.

> **Note**
> Generally you should not use a particular release, f.i. you should not set TOOLBOSCORE_AUTO_VERSION.
> Consider it only for the two use cases listed above. 

