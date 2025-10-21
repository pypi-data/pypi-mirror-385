.. highlight:: none

Installation and Usage
======================

#.  Make sure you have Python_ installed.

#.  Install the Python package ``insipid-sphinx-theme``, e.g. with pip_::

        python -m pip install insipid-sphinx-theme

    If you have installed the module already,
    you can use the ``--upgrade`` flag to get the newest release.

    .. note::

        By default, a recent Sphinx version is required and automatically
        installed when installing ``insipid-sphinx-theme``.
        Older Sphinx versions are supported to some degree
        (some features might not be rendered as in newer versions, see
        https://insipid-sphinx-theme.readthedocs.io/en/sphinx3/ and
        https://insipid-sphinx-theme.readthedocs.io/en/sphinx4/),
        but those older versions have to be installed manually
        and ``insipid-sphinx-theme`` has to be installed
        with the ``--no-deps`` flag.

#.  Edit the :file:`conf.py` file
    (just create an empty file if it doesn't exist yet,
    or use :doc:`sphinx:man/sphinx-quickstart`) and add/edit the line:

    .. code-block:: python

        html_theme = 'insipid'

#.  Make sure your source files are
    in the same directory as your :file:`conf.py`.
    If you don't have any source files yet,
    you can start with a simple :file:`index.rst`:

    .. code-block:: rst

        My Docs
        =======

        Hello, world!

    At some point, you'll probably want to have more than one page.
    You can use the :rst:dir:`toctree` directive
    to include additional pages.

#.  Run Sphinx, e.g. by using::

        python -m sphinx <source-dir> <build-dir>

    ... where ``<source-dir>`` is the directory
    that contains your :file:`conf.py`,
    and ``<build-dir>`` is the place where the generated HTML files
    should be written to.
    For example, the full command could look something like this::

        python -m sphinx doc html-files

    For more options, see :doc:`sphinx:man/sphinx-build`.


That should be it.
But there are many options (:doc:`configuration`) and customization
possibilities (:doc:`customization`) available.

.. admonition:: Alternative Usage

    It is convenient to install the theme as a Python package,
    because this way Sphinx can find it easily
    and you don't have to worry about where the theme's files are stored.
    However, the package installation is not strictly necessary
    (because the ``insipid`` theme is just a theme
    and not a full-blown Sphinx extension).
    If you don't want to install the package,
    you can instead use :confval:`html_theme_path`
    to tell Sphinx where the directory containing the ``insipid`` directory is.

    For example, you could include the insipid-sphinx-theme_ repository
    as a Git submodule in your own repository and point to that submodule
    in your :file:`conf.py`:

    .. code-block:: python

        html_theme_path = ['path-to-submodule/src/insipid_sphinx_theme']
        html_theme = 'insipid'

.. _Python: https://www.python.org/
.. _pip: https://pip.pypa.io/
.. _insipid-sphinx-theme: https://github.com/mgeier/insipid-sphinx-theme/
