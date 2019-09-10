##  Sourcing additional packages


To always have additional packages sourced, please do so directly in your ~/.bashrc (after the sourcing of
ToolBOSCore/3.2/BashSrc).

>Note   
>    At this point you may make use of ${SIT}.

    # mandatory:
    source /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.2/BashSrc
    
    # optional:
    source ${SIT}/Applications/ABC/1.0/BashSrc
    source ${SIT}/Libraries/Foo/42.0/BashSrc
    
 
###  Windows

Create a custom batch script, e.g. C:\CmdSrc.bat, to load additional packages:

    call ${SIT}/Applications/ABC/1.0/CmdSrc.bat
    call ${SIT}/Libraries/Foo/42.0/CmdSrc.bat
    
Then invoke it on your Windows console:

    c:\CmdSrc.bat