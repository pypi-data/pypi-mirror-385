Configuration
=============

.. include:: ../note.rst

By default, slidge uses all config files found in ``/etc/slidge/conf.d/*``.
You can change this using the ``SLIDGE_CONF_DIR`` env var, eg
``SLIDGE_CONF_DIR=/path/dir1:/path/dir2:/path/dir3``.

It is recommended to use ``/etc/slidge/conf.d/`` to store configuration options
common to all slidge components (eg, attachment handling, logging options,
etc.), and to specify a plugin-specific file on startup, eg:

.. code-block:: bash

    slidge -c /etc/slidge/superduper.conf

.. note::
  For the debian unofficial package, just edit the ``/etc/slidge/conf.d/common.conf`` and
  ``/etc/slidge/*.conf`` files, and use :ref:`Debian packages (systemd)` to
  launch slidge.

Command-line arguments
----------------------

.. code-block:: text

      -h, --help            show this help message and exit
      -c, --config CONFIG   Path to a INI config file. [env var: SLIDGE_CONFIG]
      --log-config LOG_CONFIG
                            Path to a INI config file to personalise logging output.
      -q, --quiet           loglevel=WARNING (unused if --log-config is specified) [env var: SLIDGE_QUIET]
      -d, --debug           loglevel=DEBUG (unused if --log-config is specified) [env var: SLIDGE_DEBUG]
      --version             show program's version number and exit


Regarding the ``--log-config`` argument, refer to the `official python documentation
<https://docs.python.org/3/library/logging.config.html#configuration-file-format>`_
for the syntax.

Other options
-------------

.. warning::

    Because of an ugly mess that will soon™ be fixed, it is impossible to use
    the config file to turn off boolean arguments that are true by default.
    As a workaround, use CLI args instead, e.g., ``--some-opt=false``.

The following options can be used:

* in a config file (see top of this page);
* as command line arguments, prepended with ``--``, e.g., ``--some-option=value``;
* as environment variables, upper case, prepended with ``SLIDGE_``,
  and with dashes substituted with underscores, e.g., ``SLIDGE_SOME_OPTION=value``.

.. config-obj:: slidge.core.config
