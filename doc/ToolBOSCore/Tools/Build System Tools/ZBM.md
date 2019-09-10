##  Zen Build Mode

![](BST-small.png)    

Be a zen-master and orchestrate complicated build scenarios with this powerful yet simple GUI.

**Features:**

* build for multiple architectures in parallel
* no need to worry about cross-compiler settings
* operator shell: execute commands locally, or on all remote hosts
* open SSH connection to build servers (right into remote working directory)
* parallel + distributed compilation
* launch developer tools
* run [software quality](../../Concepts/QualityGuidelines.md) checks
* ...

Usage:

Go to the top-level directory of your package and start the "Zen Build Mode". Within the GUI select the desired 
platform(s) to build for and press the Build button.

    $ cd MyPackage/1.0
    $ BST.py -z


![](ZenBuildMode-800x487.png)