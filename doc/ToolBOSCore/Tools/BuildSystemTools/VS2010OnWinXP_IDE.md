##  VS2010 on WinXP (IDE)         {#VS2010_WinXP_IDE}

![](BST-small.png)


###  1. Have SIT available on Windows

For a quick start we expect to have the SIT network share mapped to drive letter S:\ .

You can map network drives under "MyComputer" → "Tools" → "Map network drive".

![](MapNetworkDrive-WinXP.png)


###  2. Step into package

Open a console (cmd.exe) and navigate to your package.

![](TopLevelDirectory-WinXP.png)

###  3. Launch package configuration
     
Run buildVS2010.bat with "-c" parameter. This script auto-detects the CPU architecture (32 / 64 bit), prepares the environment and then invokes BST.py –setup.
     
This will result in a Visual Studio project file ("solution").

![](RunWindowsBuildScript-SetupOnly.png)


###  4. Open the Visual Studio solution-file (*.sln)

![](VisualStudioSolutionFile.png)
![](VisualStudioOpenDialog.png)


### 5. Switch to "release" mode and press build button

![](VisualStudioSwitchToRelease.png)


![](VisualStudioBuild.png)