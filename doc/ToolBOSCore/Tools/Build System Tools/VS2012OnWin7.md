##  VS2012 on Win7


![](BST-small.png)


### 1. Have SIT available on Windows

For a quick start we expect to have the SIT network share mapped to drive letter S:\.   
You can map network drives under "Start" → "Computer" → "Map network drive".

![](MapNetworkDrive-Win7.png)


###  2. Step into package
     
Open a console (cmd.exe) and navigate to your package.

![](TopLevelDirectory-Win7.png)


### 3. Launch build script
    
Run buildVS2012.bat. This script auto-detects the CPU architecture (32 / 64 bit), 
prepares the environment and then invokes BST.py.

![](RunWindowsBuildScript-Win7.png)

![](VisualStudio2012-Win7.png)