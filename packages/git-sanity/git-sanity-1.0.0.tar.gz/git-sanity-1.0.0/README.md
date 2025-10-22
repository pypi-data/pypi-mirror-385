# gits
多Git仓库管理工具

## gits 用法：
```
usage: gits [-h] [-v] {init,clone,sync,switch,branch,cherry-pick,push} ...

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

sub-commands:
  {init,clone,sync,switch,branch,cherry-pick,push}
                        additional help with sub-command -h
    init                initialize the projects
    clone               clone repo(s)
    sync                sync source project(s)
    switch              switch branches
    branch              list or delete branches
    cherry-pick         TODO:add repo(s)
    push                update remote refs along with associated objects
```

### 一、`gits init` 用法
```
usage: gits init [-h] [-u URL] [-d DIRECTORY]

Initialize the projects

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     the gits configuration repository
  -d DIRECTORY, --directory DIRECTORY
                        the path to init gits configuration repository
```

### 二、`gits clone` 用法
```
usage: gits clone [-h] [-g GROUP]

Clone repo(s)

options:
  -h, --help            show this help message and exit
  -g GROUP, --group GROUP
                        group to clone, default all
```

### 三、`gits sync` 用法
```
usage: gits sync [-h] [-g GROUP]

Sync source project(s)

options:
  -h, --help            show this help message and exit
  -g GROUP, --group GROUP
                        projects to sync, default all
```

### 四、`gits switch` 用法
```
usage: gits switch [-h] [-g GROUP] [-c NEW_BRANCH_NAME | -b BRANCH_NAME] [remote]

Switch branches

positional arguments:
  remote                remote name to switch branches, default origin

options:
  -h, --help            show this help message and exit
  -g GROUP, --group GROUP
                        group to switch branches, default all
  -c NEW_BRANCH_NAME, --create NEW_BRANCH_NAME
                        create a new branch named <new-branch> base on origin/HEAD
  -b BRANCH_NAME, --branch BRANCH_NAME
                        branch to switch to
```

### 五、`gits branch` 用法
```
usage: gits branch [-h] [-g GROUP] [-d DELETE | -D FORCE_DELETE] [list]

List or delete branches

positional arguments:
  list                  list branch names

options:
  -h, --help            show this help message and exit
  -g GROUP, --group GROUP
                        group to operate, default all
  -d DELETE, --delete DELETE
                        delete fully merged branch
  -D FORCE_DELETE, --DELETE FORCE_DELETE
                        delete branch (even if not merged)
```

### 六、`cherry-pick` 用法
待实现

### 七、`gits push` 用法
```
usage: gits push [-h] [-g GROUP] [-f] remote

Update remote refs along with associated objects

positional arguments:
  remote                remote branch to be pushed

options:
  -h, --help            show this help message and exit
  -g GROUP, --group GROUP
                        group to push, default all
  -f, --force           force updates
```