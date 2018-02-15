repoman
=======

    *A lot of people don't realize what's really going on.
    They view life as a bunch of unconnected incidents and things.
    They don't realize that there's this, like, lattice of
    coincidence that lays on top of everything.*

    \- Repo Man, 1984

repoman is a collection of utilities for supporting development of
software packages and their dependencies for the Fermi Gamma-Ray
Space telescope.

Getting started
===============

Repoman can check out products (container packages) and their dependency
packages. It's oriented around the concept of a workspace -- a common
folder where the products and their packages are organized in a flat
structure. You may have multiple workspaces or just one.

While you can use repoman to interact in a few ways described below with
your workspace, you'll still probably want to use plain old git when
checking in code, creating or switching branches on a single package,
and other tasks. Where repoman can really help is coordinating the checkout
of multiple existing branches across the repos, as well as reading the input
of the package manifest (packageList.txt) of the container package and
checking out the according to that specification.

Install repoman with ``pip install fermi-repoman``

After you install repoman, you may check out a package. By default, repoman
will use SSH remotes and set them up automatically for you. This may pose a
problem if you don't have SSH keys already set up.

`Github <https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/>`_
has a good guide on how to set that up.

If you'd rather use the ``https`` protocol, you'll want to use a different ``--remote-base``
parameter for the fermi-lat organization, e.g. ``--remote-base https://github.com/fermi-lat``,
or set the ``REMOTE_BASE`` environment veriable so you don't need it every time.

By default, when using repoman to check out, it will fail if there are changes
in your working copy. That way it doesn't accidentally blow out work you've maybe done
developing and haven't committed. You are encouraged to fix this yourself by either
stashing your changes or resetting your repository, but if you'd like to just force
repoman to check out changes for you, use the ``--force`` option.


.. click:: repoman.cli:cli
    :prog: repoman
    :show-nested:
