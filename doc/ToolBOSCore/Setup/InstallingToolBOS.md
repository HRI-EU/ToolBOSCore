## Installing ToolBOS on disk

>Note
>
>    For sites running multiple ToolBOS machines it is common to put the data on a network share and mount the content
>    appropriately on clients, rather than copying to each local disk individually.


* Create the following directory:
    
      $ mkdir -p /hri/sit
      
* Copy the Software Installation Tree (SIT) that you have received into the /hri/sit directory.
  Example:

      $ cp -R /media/dvd/* /hri/sit
      

* Now the following directories should exist:

    * /hri/sit/builds
    * /hri/sit/LTS
    * /hri/sit/latest (symlink to builds/latest)

