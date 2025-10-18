==================
pytest-doctestplus
==================

.. image:: https://zenodo.org/badge/104253824.svg
   :target: https://zenodo.org/badge/latestdoi/104253824
   :alt: Zenodo DOI

.. image:: https://github.com/scientific-python/pytest-doctestplus/workflows/Run%20unit%20tests/badge.svg
    :target: https://github.com/scientific-python/pytest-doctestplus/actions
    :alt: CI Status

This package contains a plugin for the `pytest`_ framework that provides
advanced doctest support and enables the testing of various text files, such
as reStructuredText (".rst"), markdown (".md"), and TeX (".tex").

.. _pytest: https://pytest.org/en/latest/


Motivation
----------

This plugin provides advanced features for testing example Python code that is
included in Python docstrings and in standalone documentation files.

Good documentation for developers contains example code. This is true of both
standalone documentation and of documentation that is integrated with the code
itself. Python provides a mechanism for testing code snippets that are provided
in Python docstrings. The unit test framework pytest provides a mechanism for
running doctests against both docstrings in source code and in standalone
documentation files.

This plugin augments the functionality provided by Python and pytest by
providing the following features:

* approximate floating point comparison for doctests that produce floating
  point results (see `Floating Point Comparison`_)
* skipping particular classes, methods, and functions when running doctests (see `Skipping Tests`_)
* handling doctests that use remote data in conjunction with the
  `pytest-remotedata`_ plugin (see `Remote Data`_)
* optional inclusion of ``*.rst`` files for doctests (see `Setup and Configuration`_)
* optional inclusion of doctests in docstrings of Numpy ufuncs

Further, ``pytest-doctestplus`` supports editing files to fix incorrect docstrings
(See `Fixing Existing Docstrings`_).

.. _pytest-remotedata: https://github.com/astropy/pytest-remotedata

Installation
------------

The ``pytest-doctestplus`` plugin can be installed using ``pip``::

    $ pip install pytest-doctestplus

It is also possible to install the latest development version from the source
repository::

    $ git clone https://github.com/scientific-python/pytest-doctestplus
    $ cd pytest-doctestplus
    $ pip install .

In either case, the plugin will automatically be registered for use with
``pytest``.

Usage
-----

Note: In lieu of ``setup.cfg``, ``pyproject.toml`` configuration is also
supported; where ``setup.cfg`` is mentioned below, replace the syntax
with TOML equivalent.

.. _setup:

Setup and Configuration
~~~~~~~~~~~~~~~~~~~~~~~

This plugin provides three command line options: ``--doctest-plus`` for enabling
the advanced features mentioned above, ``--doctest-rst`` for including
``*.rst`` files in doctest collection, and ``--doctest-ufunc`` for including
doctests in docstrings of Numpy ufuncs.

This plugin can also be enabled by default by adding ``doctest_plus = enabled``
to the ``[tool:pytest]`` section of the package's ``setup.cfg`` file.

The plugin is applied to all directories and files that ``pytest`` collects.
This means that configuring ``testpaths`` and ``norecursedirs`` in
``setup.cfg`` also affects the files that will be discovered by
``pytest-doctestplus``. In addition, this plugin provides a
``doctest_norecursedirs`` configuration variable that indicates directories
that should be ignored by ``pytest-doctestplus`` but do not need to be ignored
by other ``pytest`` features.

Using ``pytest``'s built-in ``--doctest-modules`` option will override the
behavior of this plugin, even if ``doctest_plus = enabled`` in ``setup.cfg``,
and will cause the default doctest plugin to be used. However, if for some
reason both ``--doctest-modules`` and ``--doctest-plus`` are given, the
``pytest-doctestplus`` plugin will be used, regardless of the contents of
``setup.cfg``.

``pytest-doctestplus`` respects the ``--doctest-continue-on-failure`` flag.
If set, doctests will report all failing lines, which may be useful to detect
independent errors within the same doctest. However, it is likely to generate
false positives when an early failure causes a variable later lines access to
remain unset or have an unexpected value.

This plugin respects the doctest options that are used by the built-in doctest
plugin and are set in ``doctest_optionflags`` in ``setup.cfg``. By default,
``ELLIPSIS`` and ``NORMALIZE_WHITESPACE`` are used. For a description of all
doctest settings, see the `doctest documentation
<https://docs.python.org/3/library/doctest.html#option-flags>`_.

Running Tests in Markdown Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run doctests in Markdown files, invoke pytest with the command line options
``--doctest-plus --doctest-glob '*.md'``.

If you write doctests inside `GitHub-style triple backtick fenced code blocks
<https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks#fenced-code-blocks>`_,
then in order for pytest-doctest to find and run them you need to include an
extra trailing newline inside your code blocks, like this::

    ```pycon
    >>> 1 + 2
    2

    ```

Doctest Directives
~~~~~~~~~~~~~~~~~~

The ``pytest-doctestplus`` plugin defines `doctest directives`_ that are used
to control the behavior of particular features. For general information on
directives and how they are used, consult the `documentation`_. The specifics
of the directives that this plugin defines are described in the sections below.

.. _doctest directives: https://docs.python.org/3/library/doctest.html#directives
.. _documentation: https://docs.python.org/3/library/doctest.html#directives

Sphinx Doctest Directives
~~~~~~~~~~~~~~~~~~~~~~~~~

You can use ``testsetup`` and ``testcleanup`` in Sphinx RST to run code that is
not visible in rendered document. However, due to how ``pytest-doctestplus``
works, the code within needs to be prepended by ``>>>``. For example::

  .. testsetup::

      >>> x = 42

  .. testcleanup::

      >>> del x

Floating Point Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~

Some doctests may produce output that contains string representations of
floating point values.  Floating point representations are often not exact and
contain roundoffs in their least significant digits.  Depending on the platform
the tests are being run on (different Python versions, different OS, etc.) the
exact number of digits shown can differ.  Because doctests work by comparing
strings this can cause such tests to fail.

To address this issue, the ``pytest-doctestplus`` plugin provides support for a
``FLOAT_CMP`` flag that can be used with doctests.  For example:

.. code-block:: python

  >>> 1.0 / 3.0  # doctest: +FLOAT_CMP
  0.333333333333333311

.. code-block:: python

  >>> {'a': 1 / 3., 'b': 2 / 3.}  # doctest: +FLOAT_CMP
  {'a': 0.333333, 'b': 0.666666}

When this flag is used, the expected and actual outputs are both parsed to find
any floating point values in the strings.  Those are then converted to actual
Python `float` objects and compared numerically.  This means that small
differences in representation of roundoff digits will be ignored by the
doctest.  The values are otherwise compared exactly, so more significant
(albeit possibly small) differences will still be caught by these tests.

This flag can be enabled globally by adding it to ``setup.cfg`` as in

.. code-block:: ini

    doctest_optionflags =
        NORMALIZE_WHITESPACE
        ELLIPSIS
        FLOAT_CMP

Ignoring warnings
~~~~~~~~~~~~~~~~~

If code in a doctest emits a warning and you want to make sure that warning is silenced,
you can make use of the ``IGNORE_WARNINGS`` flag. For example:

.. code-block:: python

  >>> import numpy as np
  >>> np.mean([])  # doctest: +IGNORE_WARNINGS
  np.nan

Showing warnings
~~~~~~~~~~~~~~~~

If code in a doctest emits a warning and you want to make sure that warning is
shown, you can make use of the ``SHOW_WARNINGS`` flag. This is useful when
warnings are turned into errors by pytest, and also because by default warnings
are printed to stderr. This is the opposite from ``IGNORE_WARNINGS`` so
obviously the two flags should not be used together. For example:

.. code-block:: python

  >>> import numpy as np
  >>> np.mean([])  # doctest: +SHOW_WARNINGS
  RuntimeWarning: Mean of empty slice.
  RuntimeWarning: invalid value encountered in double_scalars
  np.nan

Skipping Tests
~~~~~~~~~~~~~~

Doctest provides the ``+SKIP`` directive for skipping statements that should
not be executed when testing documentation.

.. code-block:: python

    >>> open('file.txt') # doctest: +SKIP

In Sphinx ``.rst`` documentation, whole code example blocks can be skipped with the
directive

.. code-block:: rst

    .. doctest-skip::

        >>> import asdf
        >>> asdf.open('file.asdf')

However, it is often useful to be able to skip docstrings associated with
particular functions, methods, classes, or even entire files.

Skipping All the Tests
^^^^^^^^^^^^^^^^^^^^^^

It is also possible to skip all doctests below a certain line using
a ``doctest-skip-all`` comment.  Note the lack of ``::`` at the end
of the line here.

.. code-block:: rst

    .. doctest-skip-all

       >>> import non_existing
       >>> non_existing.write_pseudo_code()
       All the doctests are skipped in the file below


Skip Unconditionally
^^^^^^^^^^^^^^^^^^^^

The ``pytest-doctestplus`` plugin provides a way to indicate that certain
docstrings should be skipped altogether. This is configured by defining the
variable ``__doctest_skip__`` in each module where tests should be skipped. The
value of ``__doctest_skip__`` should be a list of wildcard patterns for all
functions/classes whose doctests should be skipped.  For example::

   __doctest_skip__ = ['myfunction', 'MyClass', 'MyClass.*']

skips the doctests in a function called ``myfunction``, the doctest for a
class called ``MyClass``, and all *methods* of ``MyClass``.

Module docstrings may contain doctests as well. To skip the module-level
doctests::

    __doctest_skip__  = ['.', 'myfunction', 'MyClass']

To skip all doctests in a module::

   __doctest_skip__ = ['*']

Doctest Dependencies
^^^^^^^^^^^^^^^^^^^^

It is also possible to skip certain doctests depending on whether particular
dependencies are available. This is configured by defining the variable
``__doctest_requires__`` at the module level. The value of this variable is
a dictionary that indicates the modules that are required to run the doctests
associated with particular functions, classes, and methods.

The keys in the dictionary are wildcard patterns like those described above, or
tuples of wildcard patterns, indicating which docstrings should be skipped. The
values in the dictionary are lists of module names that are required in order
for the given doctests to be executed.

Consider the following example::

    __doctest_requires__ = {('func1', 'func2'): ['scipy']}

Having this module-level variable will require ``scipy`` to be importable
in order to run the doctests for functions ``func1`` and ``func2`` in that
module.

Similarly, in Sphinx ``.rst`` documentation, whole code example blocks can be
conditionally skipped if a dependency is not available.

.. code-block:: rst

    .. doctest-requires:: asdf

        >>> import asdf
        >>> asdf.open('file.asdf')

Furthermore, if the code only runs for specific versions of the optional dependency,
you can add a version check like this:

.. code-block:: rst

    .. doctest-requires:: asdf<3

        >>> import asdf
        >>> asdf.open('file.asdf')

Finally, it is possible to skip collecting doctests in entire subpackages by
using the ``doctest_subpackage_requires`` in the ``[tool:pytest]`` section of
the package's ``setup.cfg`` file. The syntax for this option is a list of
``path = requirements``, e.g.::

    doctest_subpackage_requires =
        astropy/wcs/* = scipy>2.0;numpy>1.14
        astropy/cosmology/* = scipy>1.0

Multiple requirements can be specified if separated by semicolons.

It is also possible to conditionally skip all the doctests in a narrative
documentation with ``doctest-requires-all``.

Remote Data
~~~~~~~~~~~

The ``pytest-doctestplus`` plugin can be used in conjunction with the
`pytest-remotedata`_ plugin in order to control doctest code that requires
access to data from the internet. In order to make use of these features, the
``pytest-remotedata`` plugin must be installed, and remote data access must
be enabled using the ``--remote-data`` command line option to ``pytest``. See
the `pytest-remotedata plugin documentation`__ for more details.

The following example illustrates how a doctest that uses remote data should be
marked:

.. code-block:: python

    >>> from urlib.request import urlopen
    >>> url = urlopen('http://astropy.org')  # doctest: +REMOTE_DATA

The ``+REMOTE_DATA`` directive indicates that the marked statement should only
be executed if the ``--remote-data`` option is given. By default, all
statements marked with the remote data directive will be skipped.

Whole code example blocks can also be marked to control access to data from the internet
this way:

.. code-block:: python

    .. doctest-remote-data::

        >>> import requests
        >>> r = requests.get('https://www.astropy.org')

.. _pytest-remotedata: https://github.com/astropy/pytest-remotedata
__ pytest-remotedata_

Sphinx Compatibility
~~~~~~~~~~~~~~~~~~~~

To use the additional directives when building your documentation with sphinx
you may want to enable the sphinx extension which registers these directives
with sphinx. Doing so ensures that sphinx correctly ignores these directives,
running the doctests with sphinx is not supported. To do this, add
``'pytest_doctestplus.sphinx.doctestplus'`` to your ``extensions`` list in your
``conf.py`` file.


Fixing Existing Docstrings
--------------------------
The plugin has basic support to fix docstrings, this can be enabled by
running ``pytest`` with ``--doctest-plus-generate-diff``.
Without further options, this will print out a diff and a list of files that
would be modified.  Using ``--doctest-plus-generate-diff=overwrite`` will
modify the files in-place, so it is recommended to run the check first to
verify the paths.
You may wish to review changes manually and only commit some patches e.g. using ``git commit --patch``.

The current diff generation is still very basic, for example, it does not account for
existing ``...``.  By default a diff is only generated for *failing* doctests.

In general, a mass edit may wish to focus on a specific change and
possibly include passing tests.  So you can opt-in into the behavior by
adding a hook to your ``conftest.py``::

    @pytest.hookimpl
    def pytest_doctestplus_diffhook(info):
        info["use"] = True  # Overwrite all results (even successes)
        if info["fileno"] is None:
            # E.g. NumPy has C docstrings that cannot be found, we can add
            # custom logic here to try and find these:
            info["filename"] = ...
            info["lineno"] = ...

Where ``info`` is a dictionary containing the following items:

* ``use``: ``True`` or ``False`` signalling whether to apply the diff.  This is
  set to ``False`` if a doctest succeeded and ``True`` if the doctest failed.
* ``name``: The name of the test (e.g. the function being documented)
* ``filename``: The file that contains the test (this can be wrong in certain
  situation and in that case ``test_lineno`` will be wrong as well).
* ``source``: The source code that was executed for this test
* ``test_lineno``: The line of code where the example block (or function) starts.
  In some cases, the test file cannot be found and the lineno will be ``None``,
  you can manually try to fix these.
* ``example_lineno``: The line number of the example snippet
  (individual ``>>>``).
* ``want``: The current documentation.
* ``got``: The result of executing the example.

You can modify the dictionary in-place to modify the behavior.

Please note that we assume that this API will be used only occasionally and
reserve the right to change it at any time.


Development Status
------------------

Questions, bug reports, and feature requests can be submitted on `github`_.

.. _github: https://github.com/scientific-python/pytest-doctestplus

License
-------
This plugin is licensed under a 3-clause BSD style license - see the
``LICENSE.rst`` file.
