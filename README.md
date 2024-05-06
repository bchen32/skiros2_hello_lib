###  SkiROS2 hello library

Template of a custom package for [skiros2](https://github.com/RVMI/skiros2).

### Configure steps

The renaming process below uses a common Perl tool to rename files. It can be installed with
```
sudo apt install rename
```

* Replace word "hello" with your package name:
```
cd skiros2_hello_lib
# Rename inside files
git grep -l 'hello' | xargs sed -i 's/hello/my_package_name/g'
# Rename files
find . -depth -execdir rename 's/hello/my_package_name/' '{}' \;
```
* Replace word "test_bot" with your robot name:
```
git grep -l 'test_bot' | xargs sed -i 's/test_bot/my_robot/g'
find . -depth -execdir rename 's/test_bot/my_robot_name/' '{}' \;
```
* Build your workspace
* Source your workspace
* Launch main.launch
```
roslaunch skiros2_<my_package_name>_lib main.launch
```

