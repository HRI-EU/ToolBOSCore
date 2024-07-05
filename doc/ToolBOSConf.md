## ToolBOS.conf

If ToolBOS does not detect desired values, you may override or customize certain settings via configfiles.  
They are Python files typically with simple key-value pair assignments only but might contain script logic as well.  
The content is being evaluated when loading such files.  

If a setting is not found in the current ToolBOS.conf file, it will look-up the lower priority paths/files until it was 
found otherwise fallback to the default value shipped with the ToolBOS SDK itself.

**The paths/files are searched in the following order:**

* ./ToolBOS.conf (current working directory)
* entries from additional search-paths if provided
* ${HOME}/.HRI/ToolBOS/ToolBOS.conf (user-settings)
* /etc/ToolBOS.conf (machine-wide settings by sysadmin)
* ${TOOLBOSCORE_ROOT}/etc/ToolBOS.conf (fallback / defaults)

### Commandline usage
 
You may configure your settings using ToolBOS-Config.py:

    $ ToolBOS-Config.py                                 # list all settings
    
    $ ToolBOS-Config.py -p hostPlatform                 # print host platform
    
    $ ToolBOS-Config.py -s "foo=bar"                    # add custom setting
    
