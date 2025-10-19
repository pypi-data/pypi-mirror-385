# Shutil Statement

Codeaudit checks on `shutil` use.


Reason:

It is possible that files are created outside of the path specified in the extract_dir argument, e.g. members that have absolute filenames starting with `/` or filenames with two dots `..`. 

Other implemented checks on `shutil` module methods:
* shutil.unpack_archive
* shutil.copy
* shutil.copy2
* shutil.copytree
* shutil.chown
* shutil.rmtree

Note:
* `shutil.rmtree` can be dangerous. However this call is/will be depreciated within the `shutil` module. For now Python Code Audit will check on usage.


## More information

* https://docs.python.org/3/library/shutil.html