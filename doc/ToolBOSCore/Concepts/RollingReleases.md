## Rolling releases

ToolBOS and the majority of SIT packages do not follow traditional point release cycles. Since there is no "final"
state in software there is also no physical installation media of ToolBOS or the SIT. Instead, you'll get a snapshot of 
the software at any time. Then fairly continuous small updates of the individual SIT packages will evolve the overall 
functionality over time.

### Major benefits

* avoid efforts on maintaining old versions (backporting patches, managing various customer branches → single source base)
* short time-to-market for new features (no need to wait next scheduled point release)
* easy rollback in case of trouble (few changes)
* smooth transition / upgrade over time
* no re-installation of ToolBOS or the SIT, just sync to the latest software snapshot

**See also**

[Rolling release](http://en.wikipedia.org/wiki/Rolling_Release)  
[Point release vs. rolling release: Developer, user, and security considerations](http://www.techrepublic.com/blog/security/point-release-vs-rolling-release-developer-user-and-security-considerations/4150 )  
[SIT builds](../HowTo/SITBuilds.md)
