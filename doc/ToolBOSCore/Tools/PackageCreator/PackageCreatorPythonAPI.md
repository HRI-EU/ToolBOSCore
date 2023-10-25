##  Python API

The **Package Creator** can be embedded into your Python application to create packages programmatically.


#### Example

This uses the C_Library template to create a package /tmp/test/Foo/1.0 with the category set to "Libraries/Data":

    from ToolBOSCore.Packages.PackageCreator import PackageCreator_C_Library

    values = { 'category': 'Libraries/Data' }
    pc     = PackageCreator_C_Library( 'Foo', '1.0', values, '/tmp/test' )

    pc.run()


####  "values" documentation

values must be a Python dict containing any of the following keys:

|key 	          |datatype | 	description
|-----------------|---------|----------------   
| buildRules      |	string  | Put this text verbatim in the CMakeLists.txt instead of the default build instructions. Note that if this key is specified then srcFilesPattern, exeFilesPattern, preBuildRules and postBuildRules have no effect.  
| buildRules      |	string 	| Put this text verbatim in the CMakeLists.txt instead of the default build instructions. Note that if this key is specified then srcFilesPattern, exeFilesPattern, preBuildRules and postBuildRules have no effect. 
| postBuildRules  |	string  | Put this text verbatim in the CMakeLists.txt right after the default build rules.
| srcFilesPattern |	string  | Glob-expression which shall be used for searching library source files (e.g. "src/A/*.c src/B/*.c"). Has no effect if buildRules is specified.
| exeFilesPattern |	string  | Glob-expression which shall be used for searching main program source files (e.g. "bin/*.c examples/*.c"). Has no effect if buildRules is specified.
| category        |	string  | SIT category of the package, such as "Libraries"
| category        |	string  | SIT category of the package, such as "Libraries"  
| force           |	boolean | ignore certain safety checks, f.i. overwrite existing files 

**See also**   
    PackageCreator.py