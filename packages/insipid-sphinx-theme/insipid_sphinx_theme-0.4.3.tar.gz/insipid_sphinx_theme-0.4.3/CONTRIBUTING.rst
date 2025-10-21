Contributing
============

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/mgeier/insipid-sphinx-theme/.
Contributions are always welcome!


Development Installation
------------------------

Instead of pip-installing the latest release from PyPI_, you should get the
newest development version (a.k.a. "master") from Github_::

   git clone https://github.com/mgeier/insipid-sphinx-theme.git --recursive
   cd insipid-sphinx-theme
   python -m pip install -e .

... where ``-e`` stands for ``--editable``.

When installing this way, you can quickly try other Git
branches (in this example the branch is called "another-branch")::

   git checkout another-branch

If you want to go back to the "master" branch, use::

   git checkout master

To get the latest changes from Github, use::

   git pull --ff-only

If you used the ``--recursive`` option when cloning,
the ``Font-Awesome`` submodule (containing the SVG icons)
will be checked out automatically.
If not, you can get the submodule with::

   git submodule update --init

.. _PyPI: https://pypi.org/project/insipid-sphinx-theme/
.. _Github: https://github.com/mgeier/insipid-sphinx-theme/


Building the Documentation
--------------------------

If you make changes to the documentation, you should create the HTML
pages locally using Sphinx and check if they look OK.

Initially, you might need to install a few packages that are needed to build the
documentation::

   python -m pip install --group doc

To (re-)build the HTML files, use::

   python setup.py build_sphinx

The generated files will be available in the directory ``build/sphinx/html/``.


Auto-Generated Documentation for Pull Requests
----------------------------------------------

Whenever a Pull Request (PR) is created on
https://github.com/mgeier/insipid-sphinx-theme/pull/,
the documentation is automatically built on https://readthedocs.org/.
On the PR page, find the latest commit and click on its green check mark
(or on the red "x" in case of a test failure),
look for the **readthedocs.org** entry and click on "Details"
to see the auto-generated HTML pages.
