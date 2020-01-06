# Git Submodule Hints

The STF *stf/tools* directory is implementated as a Git submodule, as these tools
are shared with other Git projects. The home repository for
*stf/tools* is
[WIPACrepo/STM32Tools](https://github.com/WIPACrepo/STM32Tools).
Though powerful, Git submodules may have some unexpected behavior.

First, a checkout of a Git respository with submodules must be performed
*recursively* including the submodules. This means the git clone invocation
is extended with the *--recurse-submodules* option, e.g.
~~~~
$ git clone --recurse-submodules git@github.com:WIPACrepo/stf.git # ssh checkout
or
$ git clone --recurse-submodules https://github.com/WIPACrepo/stf.git # https checkout
~~~~

Git also recognizes *--recursive* as a shortcut alias for *--recurse-submodules*:
~~~~
$ git clone --recursive git@github.com:WIPACrepo/stf.git
~~~~

If you only perform the basic git clone invocation, and forget the
*--recurse-submodules* option
~~~~
$ git clone git@github.com:WIPACrepo/stf.git # NOTE: WILL NOT CLONE SUBMODULES
~~~~

Then you will be left with an empty *stf/tools* directory. To fix this:
~~~~
$ git submodule init # Inform git that this workspace has submodules
$ git submodule update  # clone the submodules to the version pinned to the stf repo.
~~~~

After cloning, the *stf/tools* workspace is in a *detached HEAD* state, which
indicates the submodule version is pinned to the last version of the 
[WIPACrepo/STM32Tools](https://github.com/WIPACrepo/STM32Tools)
repository commited as the  *stf/tools* directory. The important bit here is
that submodule versions are pinned to specific versions, and do **not** track the
associated repository master branch. This leads to the often unexpected git
behavior that a top level
*git pull*
in the cloned [WIPACrepo/stf](https://github.com/WIPACrepo/stf/tree/master/stf)
cloned workspace will *not* update the submodules. An update of submodules is
often desired when a change has been made to the 
[WIPACrepo/STM32Tools](https://github.com/WIPACrepo/STM32Tools)
repository, and the updated contents are desired in the *stf/tools* directory.

Here's how to update *stf/tools* to the latest version in the 
[WIPACrepo/STM32Tools](https://github.com/WIPACrepo/STM32Tools)
repository (tip of the *master* branch). This assumes the *stf/tools* directory is
already populated with an older version of the 
[WIPACrepo/STM32Tools](https://github.com/WIPACrepo/STM32Tools)
repository:
~~~~
$ pushd stf/tools # change directory to stf/tools
$ git checkout master # leave detached HEAD state, switch to master branch
$ git pull  # pull latest version of master branch
$ popd # return to original directory
~~~~

