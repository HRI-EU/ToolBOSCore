###  SIT builds

####  What is an SIT build?

Software Installation Trees can be seen as set of software modules that have been tested and used together.
The default (latest stable) SIT is called "latest".

Once in a while incompatible changes may occur. That's the time we perform "SIT switches" in which we rebase our
development onto a new set of external libraries, or internal concepts. This means rebuilding all software and making
such more recent release the new "latest" stable SIT. The former "latest" becomes "oldstable".


####  Which releases exist, and what are they used for?

 <table>
 <tr>
     <th>oldstable</th>
     <td><ul><li>the former "stable" SIT</li>
             <li>for transition period in case you experience problems
                 with "lastest" SIT</li>
             <li>maybe useful if project deadlines do not allow software
                 changes right now</li>
             <li>the installed ToolBOS SDK typically does not get altered
                 but exceptional / important backports are possible
                 (very sparse)</li></ul></td>
 </tr>
 <tr>
     <th>latest (=&nbsp;default)</th>
     <td><ul><li>the latest stable / production release</li>
             <li>this is the place where ongoing work is published</ul></td>
 </tr>
 <tr>
     <th>testing</th>
     <td><ul><li>for in-depth testing of new features + versions</li>
             <li>you may globally install into this SIT (for testing
                 purposes)</li>
             <li>not for production use</li>
             <li>update frequency: ~2 weeks</li></ul></td>
 </tr>
 <tr>
     <th>unstable</th>
     <td><ul><li>bleeding edge / nightly build</li>
             <li>highly experimental</li>
             <li>global installations are discouraged</li>
             <li>update frequency: daily</li></ul></td>
 </tr>
 </table>
 
 
**See also**  
    http://www.debian.org/releases 
    

####  How to switch?

The desired build can be set by using the SIT_VERSION environment variable.
It needs to be set before sourcing the ToolBOSCore package.

    export SIT_VERSION=oldstable
    source /hri/sit/${SIT_VERSION}/DevelopmentTools/ToolBOSCore/3.2/BashSrc

To work permanently with this build you should set this in your ~/.bashrc . For short usage you may open an SSH
connection to localhost and temporarily set this directly in the shell.


####  What about proxy directories?

The proxy directories are independent and map to the SIT_VERSION. For example:

    $ ls -ahl ~/.HRI/sit
    [...]
    drwxr-xr-x 13 marijke marijke 4.0K 2013-05-13 11:20 latest
    drwxr-xr-x 16 marijke marijke 4.0K 2011-10-21 16:24 oldstable
    drwxr-xr-x 16 marijke marijke 4.0K 2011-07-01 15:52 testing
    
> **Attention**
> When using another SIT build for the first time you will not have a proxy directory for it, yet.
> Learn how to create a proxy directory: [Proxy Directory](../Concepts/ProxyDirectory.md)
