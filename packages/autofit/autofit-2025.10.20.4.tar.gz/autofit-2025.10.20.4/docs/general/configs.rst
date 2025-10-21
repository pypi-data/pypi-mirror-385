Configs
=======

**PyAutoFit** uses a number of configuration files that customize the default behaviour of the non-linear searches,
visualization and other aspects of **PyAutoFit**.

Descriptions of every configuration file and their input parameters are provided in the ``README.rst`` in
the `config directory of the workspace <https://github.com/Jammy2211/autofit_workspace/tree/release/config>`_


Setup
-----

By default, **PyAutoFit** looks for the config files in a ``config`` folder in the current working directory, which is
why we run autofit scripts from the ``autofit_workspace`` directory.

The configuration path can also be set manually in a script using the project **PyAutoConf** and the following
command (the path to the ``output`` folder where the results of a non-linear search are stored is also set below):

.. code-block:: bash

    from autoconf import conf

    conf.instance.push(
        new_path="path/to/config",
        output_path=f"path/to/output"
    )
